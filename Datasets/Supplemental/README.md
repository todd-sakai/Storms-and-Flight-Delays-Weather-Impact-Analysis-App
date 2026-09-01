# Supplemental Datasets — NOAA Severe Weather Data Inventory, June 2026

Two daily gridded severe-weather products from NOAA's National Centers for Environmental
Information (NCEI), used to explain weather-driven delay in the primary BTS flight data.

Source archive: <https://www.ncei.noaa.gov/pub/data/swdi/database-csv/v2/>
Downloaded 31 August 2026 as `.csv.gz` and decompressed in place.

Both files share an identical four-column schema and therefore join to the primary dataset
through the same key.

| File | Rows | Size | Distinct cells | Total events |
|---|---:|---:|---:|---:|
| `nldn-tiles-202606.csv` | 475,343 | 10.5 MB | 129,733 | 4,538,490 strikes |
| `hail-tiles-202606.csv` | 338,241 | 7.5 MB | 93,653 | 2,428,076 detections |

Both cover all 30 days of June 2026 (`20260601`–`20260630`).

## Schema (both files)

| Field | Type | Description |
|---|---|---|
| `ZDAY` | integer | UTC day, `YYYYMMDD`. 20260601–20260630 |
| `CENTERLON` | float | Grid cell centre longitude, degrees |
| `CENTERLAT` | float | Grid cell centre latitude, degrees |
| `TOTAL_COUNT` | integer | Events detected in that cell on that day |

Grid resolution is **0.1 degrees**, roughly 11 km — fine enough to resolve individual airports.
A row exists only where at least one event was detected, so `TOTAL_COUNT` is never zero and
absence of a row means "no detection", not "missing data".

### `nldn-tiles-202606.csv` — lightning

Cloud-to-ground lightning strike counts from the Vaisala National Lightning Detection Network.
`TOTAL_COUNT` ranges 1–1,481, mean 9.5. Extent: longitude −125.6 to −44.5, latitude 16.6 to 51.7
(continental US plus coastal waters).

Chosen as the primary weather signal because lightning is the most operationally direct
weather-to-delay mechanism: ramp safety rules suspend fuelling, baggage handling and pushback
when lightning strikes within roughly five miles of the field, which converts immediately into
departure delay.

### `hail-tiles-202606.csv` — hail

Hail detections from the NEXRAD Hail Detection Algorithm. `TOTAL_COUNT` ranges 1–228, mean 7.2.
Extent: longitude −167.8 to 147.9, latitude 10.5 to 67.4 — **wider than the lightning file**,
because it includes Alaska, Pacific and Caribbean radar sites and therefore crosses the
antimeridian. Any national map needs consistent extents between the two.

Chosen as a severity counterpart with a different operational response — ground stops and
airframe damage rather than ramp suspension.

## Loading these files

**The header is on line 3 and is comment-prefixed.** All three preamble lines begin with `#`,
including the one naming the columns, so a default `read_csv` will treat the first comment as the
header. Load them like this:

```python
import pandas as pd

COLS = ["ZDAY", "CENTERLON", "CENTERLAT", "TOTAL_COUNT"]

lightning = pd.read_csv("nldn-tiles-202606.csv", comment="#", names=COLS, header=None)
hail      = pd.read_csv("hail-tiles-202606.csv",  comment="#", names=COLS, header=None)

for df in (lightning, hail):
    df["date"] = pd.to_datetime(df["ZDAY"], format="%Y%m%d")
```

## Joining to the primary dataset

`ZDAY` is a **date, not a timestamp**, which is the main reason these tile products were chosen
over the raw point files. The raw files key on `ZTIME` (`YYYYMMDDHHMMSS`, UTC) while BTS times are
local to each airport with no timezone field — a per-airport, timezone-dependent join and a likely
source of silent error. Daily aggregates sidestep it entirely, at the cost of intra-day
resolution.

Two conversions are still required:

1. **Date format.** `ZDAY` is an integer `20260601`; the primary's `FlightDate` is the string
   `2026-06-01`. Parse both to datetime before joining.
2. **Coordinates.** BTS has **no latitude or longitude** — only airport codes and DOT IDs. An
   external airport coordinate lookup (e.g. OpenFlights) is required, after which each airport
   maps to its containing 0.1-degree cell by rounding.

Note the UTC day boundary: a late-evening local thunderstorm may be counted on the following
`ZDAY`.

## Known data-quality issues

1. **`hail-tiles-202606.csv` misdescribes itself.** Its header comment reads *"the count of
   Vaisala NLDN lightning strikes within a 0.1 degree grid cell"* — identical boilerplate to the
   lightning file. This is a copy-paste error in NOAA's header generation, present across their
   hail, structure and lightning tile products. The data are hail detections; only the column
   names and the filename are reliable.
2. **These are algorithm output, not verified ground reports.** The hail detection algorithm
   infers hail from radar signatures; NCEI's raw point files label themselves
   `#This file contains experimental data.` Do not treat these as confirmed hailfall, and do not
   substitute them for NCEI's Storm Events Database where ground truth matters.
3. **Coverage is limited to radar and sensor range**, so absence of detections in remote areas is
   not evidence of absence of weather.

## Licensing

NOAA open data — free to use and redistribute, with attribution requested.

**One genuine restriction:** the lightning data originates from Vaisala's commercially-operated
NLDN. Under NOAA's contract, raw flash and strike-level data are restricted to government and
military users. The 0.1-degree daily tile aggregate here is the publicly releasable derivative —
that aggregation is why the tiles product exists. This file is unrestricted, but strike-level
detail cannot be reconstructed from it.

## Not in version control

The two CSVs are gitignored — 18 MB of data that both partners download from the NCEI archive
above rather than committing. Only this README is tracked.
