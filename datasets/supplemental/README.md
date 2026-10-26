# NOAA Severe Weather Data Inventory - Data Dictionary

## Background

The data contained in these files has been extracted from the daily tile data tables of the Severe Weather Data Inventory (SWDI) database from NOAA's National Centers for Environmental Information (NCEI) data library. The time period is indicated in the name of each file; for example, nldn-tiles-202606 contains data of the sixth month of the year 2026.

## Record Layout

Below are fields in the order that they appear on the records. The two NOAA files share the same layout. `airports.csv` has its own layout and is described last.

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

### airports.csv

19 fields, in the order they appear in the CSV. 86,135 rows, one per airport, heliport or other landing site worldwide. The columns match the `airports.csv` file from [OurAirports](https://ourairports.com/data/), which is in the public domain. An empty field means the value is unknown or does not apply.

| # | Field | Description |
|---:|---|---|
| 1 | `id` | Internal OurAirports record number. Unique, 2 to 611,023 |
| 2 | `ident` | Site identifier: the ICAO code when one exists, else a local or generated code. Unique |
| 3 | `type` | Site type: `small_airport` (42,746), `heliport` (23,224), `closed` (13,548), `medium_airport` (4,106), `seaplane_base` (1,273), `large_airport` (1,175), `balloonport` (63) |
| 4 | `name` | Site name |
| 5 | `latitude_deg` | Latitude, decimal degrees. -90.0 to 83.1 |
| 6 | `longitude_deg` | Longitude, decimal degrees. -179.9 to 180.0 |
| 7 | `elevation_ft` | Elevation above sea level, feet. -1,266 to 17,372. Empty in 14,950 rows |
| 8 | `continent` | Two-letter continent code: `NA`, `SA`, `EU`, `AS`, `AF`, `OC`, `AN` |
| 9 | `iso_country` | ISO 3166-1 two-letter country code. 247 values; `US` has 32,668 rows |
| 10 | `iso_region` | ISO 3166-2 region code, for example `US-TX` |
| 11 | `municipality` | Main town or city served. Empty in 4,745 rows |
| 12 | `scheduled_service` | `yes` if the site has scheduled airline service (4,335 rows), else `no` |
| 13 | `icao_code` | Four-letter ICAO code. Filled in 10,530 rows |
| 14 | `iata_code` | Three-letter IATA code. Filled in 9,054 rows |
| 15 | `gps_code` | Code used in GPS databases. Filled in 44,440 rows |
| 16 | `local_code` | National code, for example the FAA identifier in the US. Filled in 36,108 rows |
| 17 | `home_link` | URL of the site's website. Filled in 4,767 rows |
| 18 | `wikipedia_link` | URL of the site's Wikipedia article. Filled in 16,755 rows |
| 19 | `keywords` | Other names and search terms, comma-separated. Filled in 21,771 rows |
