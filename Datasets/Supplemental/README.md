# NOAA Severe Weather Data Inventory - Data Dictionary

## Background

The data contained in these compressed files has been extracted from the Severe Weather Data Inventory (SWDI) maintained by NOAA's National Centers for Environmental Information, retrieved from https://www.ncei.noaa.gov/pub/data/swdi/database-csv/v2/ on 31 August 2026. The time period is indicated in the name of each file; for example, nldn-tiles-202606 contains data of the sixth month of the year 2026. Both files cover all 30 days of June 2026.

Each record is one grid cell on one day. Events are aggregated onto a 0.1-degree latitude/longitude grid, roughly 11 kilometres, and summed over the UTC day. A record exists only where at least one event was detected, so TOTAL_COUNT is never zero and the absence of a record means no detection rather than missing data. Because the day boundary is UTC, a late-evening local storm may be counted on the following ZDAY.

Two files are used. nldn-tiles-202606.csv holds cloud-to-ground lightning strike counts from the Vaisala National Lightning Detection Network: 475,343 records across 129,733 distinct cells, totalling 4,538,490 strikes, spanning longitude -125.6 to -44.5 and latitude 16.6 to 51.7. hail-tiles-202606.csv holds hail detections from the NEXRAD Hail Detection Algorithm: 338,241 records across 93,653 cells, totalling 2,428,076 detections, spanning longitude -167.8 to 147.9 and latitude 10.5 to 67.4. The hail extent is wider because it includes Alaska, Pacific and Caribbean radar sites and crosses the antimeridian, so national maps require consistent extents between the two.

Three characteristics of these files affect how they must be read. First, each file opens with three comment lines prefixed by a hash character, and the third of those is the header naming the columns, so a reader that assumes a header on the first line will misparse the file. Second, the header comment on hail-tiles-202606.csv incorrectly describes its contents as Vaisala NLDN lightning strikes; this is a copy-paste error in NOAA's header generation, present across their hail, structure and lightning tile products, and only the column names and the file name are reliable. Third, these are algorithm outputs rather than verified ground reports, limited to sensor and radar range, and should not be substituted for NCEI's Storm Events Database where confirmed observations are required.

ZDAY is a date rather than a timestamp, which is why these tile products were selected over the raw point files. The raw files key on ZTIME in UTC to the second, while the primary flight data records times local to each airport with no timezone field, making that join timezone-dependent per airport. Joining these files to the primary dataset still requires converting the integer ZDAY to a date to match FlightDate, and supplying airport coordinates from an external source, since the primary dataset carries airport codes but no latitude or longitude.

These data are distributed by NOAA as open data with attribution requested. One restriction applies: the lightning observations originate from Vaisala's commercially operated network, and under NOAA's contract the raw flash and strike-level data are available only to government and military users. The daily tile aggregate here is the publicly releasable derivative, which is why the tiles product exists. This file carries no restriction, but strike-level detail cannot be reconstructed from it.

The two CSV files are excluded from version control. Both partners download them from the archive linked above.

## Record Layout

Below are fields in the order that they appear on the records. Both files share the same layout.

### nldn-tiles-202606.csv

4 fields, in the order they appear in the CSV.

| # | Field | Description |
|---:|---|---|
| 1 | `ZDAY` | UTC day on which the strikes were recorded, as an integer in YYYYMMDD form. 20260601 to 20260630 |
| 2 | `CENTERLON` | Longitude of the grid cell centre, decimal degrees. -125.6 to -44.5 |
| 3 | `CENTERLAT` | Latitude of the grid cell centre, decimal degrees. 16.6 to 51.7 |
| 4 | `TOTAL_COUNT` | Cloud-to-ground lightning strikes detected in that cell on that day. 1 to 1,481, mean 9.5 |

### hail-tiles-202606.csv

4 fields, in the order they appear in the CSV.

| # | Field | Description |
|---:|---|---|
| 1 | `ZDAY` | UTC day on which the detections were recorded, as an integer in YYYYMMDD form. 20260601 to 20260630 |
| 2 | `CENTERLON` | Longitude of the grid cell centre, decimal degrees. -167.8 to 147.9 |
| 3 | `CENTERLAT` | Latitude of the grid cell centre, decimal degrees. 10.5 to 67.4 |
| 4 | `TOTAL_COUNT` | Hail detections in that cell on that day. 1 to 228, mean 7.2 |
