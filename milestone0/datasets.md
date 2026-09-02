# Dataset Decision Log

Running notes on datasets explored for the Fusion project, and why each was chosen or rejected.
Newest decisions at the bottom.

## Primary dataset

**BTS Reporting Carrier On-Time Performance, June 2026**
(`On_Time_Reporting_Carrier_On_Time_Performance_(1987_present)_2026_6.csv`)

Source: US DOT Bureau of Transportation Statistics, TranStats On-Time database.

109 fields (requirement is >=5), six of them temporal (`FlightDate`, `Year`,
`Quarter`, `Month`, `DayofMonth`, `DayOfWeek`, plus scheduled/actual departure and arrival
times). Real observational data self-reported by carriers under 14 CFR Part 234 - not synthetic.
Fully documented: BTS ships a `readme.html` data dictionary, converted to
`Datasets/Primary/README.md` and verified field-for-field against the actual CSV header (109
documented fields, 109 non-empty header cells, order matches exactly).

## Supplemental datasets

**Daily lightning strike counts, June 2026**
(`nldn-tiles-202606.csv`)

Source: NOAA NCEI Severe Weather Data Inventory CSV archive.

475,343 rows, 4 fields, 10.5 MB.
Selected first because lightning is the most operationally direct weather-to-delay mechanism
available: FAA and airline ramp-safety rules suspend fuelling, baggage handling and pushback when
lightning strikes within roughly five miles of the field, which converts immediately into
departure delay. The 0.1-degree grid (~11 km) resolves individual airports. Critically, the
`ZDAY` key is a **date**, not a timestamp - so it joins to `FlightDate` with no timezone
conversion.

**Daily hail detection counts, June 2026**
(`hail-tiles-202606.csv`)

Source: NOAA NCEI Severe Weather Data Inventory CSV archive.

338,241 rows, 4 fields, 7.5 MB.
Selected as a severity counterpart with a distinct operational response (ground stops and
airframe damage, versus ramp suspension). Identical schema to the lightning file, so both join
through the same key. June's peak severe season makes hail worth including; in a late-summer
month it would have been much sparser.


## Action items

- **BTS has no coordinates** - only airport codes and DOT IDs. An external airport lat/lon lookup
  (e.g. OpenFlights) is required before any spatial join to the weather grids can work.


## Research questions
1. How does the daily volume of lightning near an airport relate to that airport's mean departure delay?
2. Which of the 351 airports show the strongest weather-delay sensitivity, and does that track their geography?
3. Does BTS's own WeatherDelay attribution agree with independently observed lightning and hail activity on the same date and location?
4. How do the five delay causes shift in composition on days with severe weather versus clear days?
5. Do hail days and lightning days produce different operational responses (Cancellations versus delays)?
6. How far does weather disruption propagate through LateAircraftDelay to airports with no local severe weather?
7. Which carriers absorb weather disruption best, controlling for their route geography?
