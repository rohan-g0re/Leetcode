"""Unit 19 task — grouping, joining, time series.

Eight functions built on four real datasets that were saved from live APIs.
Together they walk the three questions from the lesson: per category, combined
with, and over time.

Datasets:
  frankfurter_series.json    daily FX rates, Jan-Mar 2024 (weekends missing)
  worldbank_population.json  population per country per year, 2018-2023
  worldbank_countries.json   country -> region lookup, to join against
  hn_search_python.json      stories with timestamps

Work through them in order. The first two build a frame and summarise it, the
middle three join two sources together and measure change, and the last two
put the result on a clean time axis and write it to disk.

Each docstring names the output columns and their order, and the tests check
exactly that. Treat those column lists as the specification rather than as a
suggestion — most of the failures you will hit are a column in the wrong place
or an index you forgot to reset, not arithmetic.

This is the last unit before FastAPI. When you finish it you can take a live
endpoint all the way to a saved, aggregated, joined report -- which is the
whole of Capstone A.

Run:  python -m pytest test_task.py -v
      python task.py
"""

import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
FIXTURES = HERE.parent / "fixtures"


def load_json(name):
    """Read fixtures/<name>.json and return the parsed data.

    Provided for you — you do not have to write this one. It opens the named
    file from the shared fixtures folder and parses it, so `load_json("hn_search_python")`
    hands you back the dictionaries and lists that were saved from a real API
    response. It stands in for the network call you would make in a live
    interview, so the rest of this file is about the analysis rather than the
    fetching.
    """
    return json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))


def fx_frame(payload):
    """Turn a Frankfurter time-series response into a long DataFrame.

    Frankfurter is a free currency-rate API. It replies with one dictionary
    keyed by date, and inside each date another dictionary keyed by currency.
    Two levels of nesting, and no rows anywhere:

    Input:
        {"amount": 1.0, "base": "USD",
         "rates": {"2024-01-02": {"EUR": 0.9, "GBP": 0.78}, ...}}

    Your job is to flatten that into one row per date-and-currency pair.

    Output columns, in order: date, currency, rate
      - date     UTC-aware datetime64
      - currency string
      - rate     float
    Sorted by date then currency, index reset.

    An empty or missing "rates" gives an empty frame with those columns.

    "Long format" -- one row per (entity, measure) pair -- is what groupby,
    merge and plotting all expect. Getting data into long format early is
    most of the work.

    That last paragraph is worth slowing down on, because it names the shape
    you are aiming at for the rest of your career. Long format means every
    row is one observation, and the thing being measured lives in a column
    rather than in a column name. Here that is: this currency, on this day,
    had this rate. The alternative — a column per currency, which is what the
    API is closer to — is called wide format, and it looks tidier to a human
    while being much harder to work with, because "group by currency" needs
    currency to be a value you can group on rather than a heading. groupby,
    merge and every plotting library all assume long. Reshaping into it early
    is genuinely most of the work in a data task, and once you are there the
    analysis tends to be three lines.

    Two dtype details, both of which are unit 18 paying off. Parse the dates
    with utc=True so the column is a real tz-aware datetime and the .dt
    accessors work later; the two functions after this one depend on it
    entirely. And push the rates through pd.to_numeric, because a rate that
    arrives as text will happily sort and print and then give you nonsense
    the moment you take a mean of it.

    The empty case matters too. A time-series endpoint asked for a range with
    no data in it returns a response with no rates, and every function
    downstream of this one should get a frame with the right columns and zero
    rows rather than a crash.
    """
    # TODO
    raise NotImplementedError


def monthly_fx_stats(df):
    """Per currency per month statistics over the fx frame.

    Take the long frame you just built and summarise it: for each currency,
    for each calendar month, how many observations there were and what the
    rate did. This is a two-key groupby with named aggregation, which in SQL
    you would write as GROUP BY currency, month with a handful of aggregate
    functions in the SELECT list.

    Columns, in order: currency, month, days, mean_rate, min_rate, max_rate,
                       change_pct

      month       "YYYY-MM" string
      days        number of observations in that month
      mean_rate   rounded to 4dp
      min_rate / max_rate  rounded to 4dp
      change_pct  ((last rate of the month - first rate) / first) * 100,
                  rounded to 2dp, using the chronologically first and last
                  observation within the month

    Sorted by currency then month ascending. Index reset.

    Hint: sort by date first, then "first"/"last" inside agg pick up the
    chronological ends rather than whatever order the rows happened to be in.

    That hint is the whole correctness story of this function, so here it is
    spelled out. The "first" and "last" aggregate functions do not know
    anything about dates. They hand you whatever row happens to be sitting at
    the top and the bottom of each group, in whatever order the rows arrived
    in. If the frame is not sorted by date, "the first rate of the month" is
    whichever day landed first in the file — and change_pct then measures the
    change between two arbitrary days while looking perfectly reasonable. Call
    sort_values("date") before you group, and only then do those two functions
    mean what their names say.

    A second thing worth doing deliberately: change_pct needs the first and
    last rate, but they are not among the seven output columns. Aggregate them
    anyway, under any names you like, compute change_pct from them, and then
    select the seven columns you actually want — which drops the two helpers
    for free. Computing an intermediate and then dropping it is normal and
    much easier to read than trying to do it in one expression.

    Note also that days uses "size" rather than "count", so it counts every
    row in the month. Here they would agree, since the rates are never null,
    but the habit of choosing between them on purpose is the one to build.
    """
    # TODO
    raise NotImplementedError


def fill_missing_days(df, currency):
    """Reindex one currency's rates onto EVERY calendar day in its range.

    Filter the frame down to one currency, then stretch it out so that every
    single calendar day between its first and last observation has a row —
    including the days the market was shut and no rate was published.

    Return a DataFrame with columns: date, rate, filled
      - one row per calendar day from the first to the last observed date
      - rate is carried forward from the most recent observation
      - filled is True for days that were not in the input

    The FX data has no weekend rows, so this turns roughly 64 trading days
    into roughly 90 calendar days. Whether to do that is a real analytical
    decision -- for "average rate per month" it changes the answer -- and the
    "filled" column exists so the caller can tell which is which.

    Sit with that middle sentence, because this is the function in the file
    where the technique is easy and the judgement is not. Forward-filling the
    weekends is defensible: the rate on Saturday genuinely was Friday's rate,
    in the sense that nothing traded to change it. It is also distorting: you
    have just given every Friday three times the weight of every Tuesday in
    the monthly average, so the mean you print afterwards is a different
    number from the one you would have printed before. Neither answer is
    wrong. Publishing one without knowing you chose it is. That is why the
    function does not quietly do the fill and hand back two columns — the
    "filled" flag exists so that whoever uses this can separate what was
    observed from what was invented, and can say so in the report.

    An unknown currency gives an empty frame with those columns.

    One ordering detail that catches people: capture the set of dates you
    actually observed BEFORE you resample. Once the frame has been stretched
    to daily, the invented rows look exactly like the real ones and there is
    no way to tell them apart any more.

    Look up: df.set_index("date"), .resample("D"), .ffill(), .reset_index().
    """
    # TODO
    raise NotImplementedError


def population_with_regions():
    """Join population records to their region, and aggregate.

    1. Build the population frame from worldbank_population.json:
         country_code, country_name, year, population
       (drop rows with a blank country code; population may be null)
    2. Build a lookup from worldbank_countries.json:
         country_code -> region
       (drop rows with a blank region)
    3. LEFT join population onto the lookup, keeping every population row.
    4. Return columns, in order:
         country_code, country_name, region, year, population

    Rows whose country code has no region entry keep a null region rather
    than being dropped -- you want to be able to count them.

    That is the reason for how="left" and it is worth saying out loud. An
    inner join would give you a frame with no null regions at all, which
    looks cleaner and is worse, because the countries you failed to match
    would simply be gone and nothing would tell you how many there were. A
    left join keeps them, marked with a null, where merged["region"].isna()
    .sum() can count them in one line. Filter them out afterwards if you want
    to — deliberately, and knowing the number.

    Sorted by country_code then year. Index reset.

    Before merging, assert the lookup is unique on country_code. A duplicate
    there would silently multiply your population rows.

    The two assertions here are as much the point of the exercise as the merge
    is, so write both. The first, before the merge, checks cardinality: if the
    lookup has two rows for one country code, then every population row for
    that country comes back twice, your totals double, and pandas does not
    complain even slightly. The second, after the merge, checks that the row
    count is unchanged — which for a left join against a unique key it always
    should be. Two cheap lines that catch the most common join bug there is,
    and "let me confirm the join key is unique on the right" is a sentence
    worth having ready in an interview.

    Build the two frames with a small helper function each rather than inline.
    The population frame is essentially unit 18's, and separating it out means
    you can print each side and check it before you try to combine them.
    """
    # TODO
    raise NotImplementedError


def region_population_by_year(df):
    """Total population per region per year.

    Now that every population row carries a region, roll them up: one row per
    region per year, with a headcount of contributing countries and the total.
    A two-key groupby with named aggregation, exactly the form from section 3
    of the lesson.

    Columns, in order: region, year, countries, total_population
      countries         number of rows contributing a non-null population
      total_population  sum of population, as an int

    Rows with a null region OR a null population are excluded.
    Sorted by region then year ascending. Index reset.

    Drop those two kinds of null yourself, up front, rather than relying on
    what groupby happens to do. groupby would silently discard the null-region
    rows anyway — that is its default — but doing it explicitly means the
    behaviour is visible in your code instead of hidden in a default, and it
    also handles the null populations, which groupby would happily keep and
    sum around. Once the filtering is explicit, "countries" is just a count of
    the surviving rows.

    One dtype wrinkle at the end. If the population column is a nullable
    Int64 (capital I, unit 18's type that can hold missing values), the sum
    stays nullable too and prints oddly. Cast total_population to plain int64
    once the nulls are gone, since at that point there is nothing left for the
    nullable type to hold.
    """
    # TODO
    raise NotImplementedError


def population_growth(df, region):
    """Year-over-year growth for one region.

    Levels are rarely the interesting part; change is. This function takes one
    region's yearly totals and puts each year next to the year before it, both
    as an absolute difference and as a percentage.

    Take the output of region_population_by_year, filter to one region, and
    return columns: year, total_population, change, change_pct

      change      absolute difference from the previous year (NaN for the
                  first year)
      change_pct  percentage difference from the previous year, 2dp
                  (NaN for the first year)

    Sorted by year ascending, index reset. An unknown region gives an empty
    frame with those four columns.

    Look up: Series.diff() and Series.pct_change().

    Those two do the whole job in a line each, and both give you NaN for the
    first row automatically — there is no previous year to compare against, so
    NaN is the honest answer rather than a hole to plug with zero. Resist the
    urge to fill it; a zero there would read as "no growth", which is a claim
    you cannot support.

    Sort by year before you call either of them. diff and pct_change compare
    each row with the row physically above it, not with the row whose year is
    one lower, so on an unsorted frame they compute confident nonsense. This
    is the same trap as "first"/"last" in monthly_fx_stats, and it is the most
    reliable way to get a wrong answer in this entire unit.

    pct_change returns a fraction: 0.0102 means one percent. Multiply by 100
    before rounding to 2dp, or your percentages will all round to zero.

    Handle the unknown region case explicitly. Filtering to a region nobody
    has heard of leaves you with an empty frame, and diff on nothing gives
    nothing, so the risk is not a crash — it is returning a frame with the
    wrong columns that fails a test three steps later.
    """
    # TODO
    raise NotImplementedError


def stories_per_month(hits):
    """Count Hacker News stories per calendar month, with no gaps.

    Input is the raw list of hits (each has "created_at" and "points").
    Return columns, in order: month, stories, total_points

      month          "YYYY-MM" string
      stories        number of stories that month (0 for empty months)
      total_points   sum of points that month (0 for empty months)

    Every month between the earliest and latest story must appear, including
    months with no stories. That is the difference between resample and a
    plain groupby, and it is why the shape of a sparse time series is so
    often reported wrong.

    These fifty stories are spread thinly across about twelve years, so a
    groupby on a month string would return roughly forty rows and resample
    returns a hundred and forty-three. The extra hundred are the months where
    nobody posted, and they are not padding — they are the finding. A chart
    built from the groupby version draws a continuous line and implies steady
    activity; the resample version shows the gaps that are actually there. A
    missing bar and a zero bar mean different things, and reporting the first
    as though it were the second is the single most common way a sparse time
    series gets described wrongly.

    Use resample("MS") — month START — rather than "ME". Both bucket the same
    rows, but "MS" labels each bucket with the first day of the month, which
    is what lines up one-to-one with the "YYYY-MM" strings you then format and
    with a period range built over the same span. "ME" formats to the same
    string while being a different index underneath, and that mismatch turns
    into an off-by-one you cannot see. (While you are here: "M" and "Y" were
    renamed to "ME" and "YE" in pandas 2.2, so older examples online now emit
    a deprecation warning. That is the example being old, not you being wrong.)

    Aggregate with size for the count and sum for the points, and the empty
    months come out as 0 rather than NaN, which is what the columns are
    supposed to mean.

    Sorted by month ascending, index reset.
    """
    # TODO
    raise NotImplementedError


def save_report(df, path, fmt="csv"):
    """Write a DataFrame to disk and return the number of rows written.

    The last step of the pipeline, and the one nobody practises.

    fmt "csv"   -> to_csv, no index column
    fmt "json"  -> to_json, orient="records", indent=2, dates as ISO strings
    Anything else raises ValueError naming the bad format.

    Create the parent directory if it does not exist.

    "Save the result somewhere" is the last step of almost every take-home,
    and index=False is the detail people forget.

    Here is what forgetting it does. pandas writes the index as an extra
    leading column with no header, so your CSV opens with an anonymous column
    of 0, 1, 2, 3 down the left. It is meaningless — it is just the row
    numbers your frame happened to have after the last reset_index — and it is
    the first thing a reviewer notices, because it makes the file look like
    something that was dumped rather than produced. Pass index=False and the
    header row is exactly your columns.

    For JSON, orient="records" is what produces the list-of-flat-dictionaries
    shape from unit 04 — the one every consumer expects and the one FastAPI
    will hand back over HTTP in unit 20. date_format="iso" writes timestamps
    as readable ISO strings rather than as milliseconds since 1970, which is
    the default and which nobody can read.

    Raise ValueError with the offending format in the message rather than a
    bare "bad format". The person reading that traceback needs to know which
    string was wrong, and they may well be you at some distance in time.

    Two small things: create the parent directory first, since writing into a
    folder that does not exist fails, and return the row count so the caller
    can print "wrote 48 rows" without reopening the file.
    """
    # TODO
    raise NotImplementedError


if __name__ == "__main__":
    fx = fx_frame(load_json("frankfurter_series"))
    print(monthly_fx_stats(fx).to_string(index=False))
    print()

    filled = fill_missing_days(fx, "EUR")
    print(f"EUR: {len(fx[fx.currency == 'EUR'])} observed -> {len(filled)} calendar days")
    print()

    pop = population_with_regions()
    by_region = region_population_by_year(pop)
    print(by_region.head(8).to_string(index=False))
    print()
    print(population_growth(by_region, "South Asia").to_string(index=False))
