# NOAA Severe Weather Data Inventory - Data Dictionary

## Background

The data contained in these files has been extracted from the daily tile data tables of the Severe Weather Data Inventory (SWDI) database from NOAA's National Centers for Environmental Information (NCEI) data library. The time period is indicated in the name of each file; for example, nldn-tiles-202606 contains data of the sixth month of the year 2026.

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
