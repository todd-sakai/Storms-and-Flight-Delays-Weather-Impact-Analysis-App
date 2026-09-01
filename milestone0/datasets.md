# Dataset Decision Log

Running notes on datasets explored for the Fusion project, and why each was chosen or rejected.
Newest decisions at the bottom.

## Primary dataset

**Chosen: BTS Reporting Carrier On-Time Performance, June 2026**
(`On_Time_Reporting_Carrier_On_Time_Performance_(1987_present)_2026_6.csv`)

Source: US DOT Bureau of Transportation Statistics, TranStats On-Time database.

Why it qualifies: 109 fields (requirement is >=5), six of them temporal (`FlightDate`, `Year`,
`Quarter`, `Month`, `DayofMonth`, `DayOfWeek`, plus scheduled/actual departure and arrival
times). Real observational data self-reported by carriers under 14 CFR Part 234 - not synthetic.
Fully documented: BTS ships a `readme.html` data dictionary, converted to
`Datasets/Primary/README.md` and verified field-for-field against the actual CSV header (109
documented fields, 109 non-empty header cells, order matches exactly).

### Scope decisions

1. **Started with all 12 months of 2025** (~3.0 GB, 7,001,619 rows). Rejected as unnecessarily
   large for a one-semester project; the analysis does not need multi-month seasonality.
2. **Considered August 2026, rejected on availability.** BTS publishes roughly two months in
   arrears. As of 2026-08-31 the latest available month was June 2026, released 2026-08-12;
   August 2026 will not appear until approximately mid-October. Verified against the BTS
   newsroom release announcement before committing.
3. **Settled on June 2026** - the most recent month that exists. 607,577 rows, 275 MB, 30 days,
   12 carriers, 351 airports. June is also the peak of the US organised severe-weather season,
   which maximises signal for a weather-focused study.

## Supplemental datasets

All candidates came from the NOAA NCEI Severe Weather Data Inventory CSV archive:
<https://www.ncei.noaa.gov/pub/data/swdi/database-csv/v2/>

### Chosen

**`nldn-tiles-202606.csv` - daily lightning strike counts.** 475,343 rows, 4 fields, 10.5 MB.
Selected first because lightning is the most operationally direct weather-to-delay mechanism
available: FAA and airline ramp-safety rules suspend fuelling, baggage handling and pushback when
lightning strikes within roughly five miles of the field, which converts immediately into
departure delay. The 0.1-degree grid (~11 km) resolves individual airports. Critically, the
`ZDAY` key is a **date**, not a timestamp - so it joins to `FlightDate` with no timezone
conversion.

**`hail-tiles-202606.csv` - daily hail detection counts.** 338,241 rows, 4 fields, 7.5 MB.
Selected as a severity counterpart with a distinct operational response (ground stops and
airframe damage, versus ramp suspension). Identical schema to the lightning file, so both join
through the same key. June's peak severe season makes hail worth including; in a late-summer
month it would have been much sparser.

### Rejected

| Dataset | June 2026 size | Reason rejected |
|---|---|---|
| `structure` | 155 MB gz (>1.5 GB raw) | Richest storm-cell attributes, but disproportionate to the project, and generic cell structure is less tied to airport operations than lightning or hail |
| `mda` (mesocyclone) | 4.0 MB | Mesocyclones are a tornado precursor - a step removed from anything that grounds an aircraft |
| `tvs` (tornado vortex signature) | 201 KB | Far too sparse. Tornado signatures near major airports are rare enough that the join would yield near-zero matches |
| `meso` | n/a | Archive ends at 2010 - no 2026 data exists |
| `plsr` | n/a | Archive ends at 2015 - no 2026 data exists |
| `hail` (raw point data) | 40 MB | Considered seriously. Carries `MAXSIZE`, `PROB` and `SEVPROB`, turning "was there hail" into "how big". Passed over in favour of the tiles version for schema consistency and a simpler join; **worth revisiting** if intensity becomes a needed variable |

### Rejected approach

**Joining on raw point timestamps.** The raw point files key on `ZTIME` in
`YYYYMMDDHHMMSS` **UTC**, while BTS times are local to each airport with no timezone field. That
join is timezone-dependent per airport and a likely source of silent error. The daily tile
aggregates avoid the problem entirely at the cost of intra-day resolution.

## Data quality findings

Recorded during selection, all verified directly against the files:

1. **`hail-tiles-202606.csv` misdescribes itself.** Its header comment reads *"the count of
   Vaisala NLDN lightning strikes within a 0.1 degree grid cell"* - identical boilerplate to the
   lightning file. This is a copy-paste error in NOAA's header generation, present across their
   hail, structure and lightning tile files. The data are hail detections; only the column names
   and filename are reliable.
2. **All SWDI tile files put the header on line 3**, prefixed with `#` like the two comment lines
   above it. A default `read_csv` will treat the first comment as column names. Load with
   `comment="#"` and supply `names=` explicitly.
3. **The BTS header ends in a trailing comma**, producing a phantom empty 110th column that
   pandas names `Unnamed: 110`.
4. **Delay-cause fields are not missing at random.** `CarrierDelay`, `WeatherDelay`, `NASDelay`,
   `SecurityDelay` and `LateAircraftDelay` are populated for only 153,037 of 607,577 rows,
   because BTS attributes causes only when arrival delay reaches 15 minutes. Treating those nulls
   as zero is a modelling decision, not a cleaning step.
5. **The BTS `readme.html` documents `FlightDate` as `yyyymmdd`; the data is actually
   `YYYY-MM-DD`.**
6. **Spatial extents differ.** Lightning tiles cover the continental US (lon -125.6 to -44.5).
   Hail tiles extend to Alaska, Pacific and Caribbean radar sites (lon -167.8 to 147.9), crossing
   the antimeridian. Any national map needs consistent extents.

## Open items

- **BTS has no coordinates** - only airport codes and DOT IDs. An external airport lat/lon lookup
  (e.g. OpenFlights) is required before any spatial join to the weather grids can work.
- Confirm the actual download date of the primary file. Its filesystem timestamp (2026-08-12)
  matches the BTS release date rather than necessarily the download.
