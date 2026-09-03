# BTS Reporting Carrier On-Time Performance - Data Dictionary

## Background

The data contained in the file has been extracted from the Reporting Carrier On-Time Performance (1987-present) data table of the "On-Time" database from the TranStats data library. The time period is indicated in the name of the compressed file; for example, XXX_XXXXX_2001_1 contains data of the first month of the year 2001.

## Record Layout

109 fields, in the order they appear in the CSV.

| # | Field | Description |
|---:|---|---|
| 1 | `Year` | Year |
| 2 | `Quarter` | Quarter (1-4) |
| 3 | `Month` | Month |
| 4 | `DayofMonth` | Day of Month |
| 5 | `DayOfWeek` | Day of Week |
| 6 | `FlightDate` | Flight Date (yyyymmdd) |
| 7 | `Reporting_Airline` | Unique Carrier Code. When the same code has been used by multiple carriers, a numeric suffix is used for earlier users, for example, PA, PA(1), PA(2). Use this field for analysis across a range of years. |
| 8 | `DOT_ID_Reporting_Airline` | An identification number assigned by US DOT to identify a unique airline (carrier). A unique airline (carrier) is defined as one holding and reporting under the same DOT certificate regardless of its Code, Name, or holding company/corporation. |
| 9 | `IATA_CODE_Reporting_Airline` | Code assigned by IATA and commonly used to identify a carrier. As the same code may have been assigned to different carriers over time, the code is not always unique. For analysis, use the Unique Carrier Code. |
| 10 | `Tail_Number` | Tail Number |
| 11 | `Flight_Number_Reporting_Airline` | Flight Number |
| 12 | `OriginAirportID` | Origin Airport, Airport ID. An identification number assigned by US DOT to identify a unique airport. Use this field for airport analysis across a range of years because an airport can change its airport code and airport codes can be reused. |
| 13 | `OriginAirportSeqID` | Origin Airport, Airport Sequence ID. An identification number assigned by US DOT to identify a unique airport at a given point of time. Airport attributes, such as airport name or coordinates, may change over time. |
| 14 | `OriginCityMarketID` | Origin Airport, City Market ID. City Market ID is an identification number assigned by US DOT to identify a city market. Use this field to consolidate airports serving the same city market. |
| 15 | `Origin` | Origin Airport |
| 16 | `OriginCityName` | Origin Airport, City Name |
| 17 | `OriginState` | Origin Airport, State Code |
| 18 | `OriginStateFips` | Origin Airport, State Fips |
| 19 | `OriginStateName` | Origin Airport, State Name |
| 20 | `OriginWac` | Origin Airport, World Area Code |
| 21 | `DestAirportID` | Destination Airport, Airport ID. An identification number assigned by US DOT to identify a unique airport. Use this field for airport analysis across a range of years because an airport can change its airport code and airport codes can be reused. |
| 22 | `DestAirportSeqID` | Destination Airport, Airport Sequence ID. An identification number assigned by US DOT to identify a unique airport at a given point of time. Airport attributes, such as airport name or coordinates, may change over time. |
| 23 | `DestCityMarketID` | Destination Airport, City Market ID. City Market ID is an identification number assigned by US DOT to identify a city market. Use this field to consolidate airports serving the same city market. |
| 24 | `Dest` | Destination Airport |
| 25 | `DestCityName` | Destination Airport, City Name |
| 26 | `DestState` | Destination Airport, State Code |
| 27 | `DestStateFips` | Destination Airport, State Fips |
| 28 | `DestStateName` | Destination Airport, State Name |
| 29 | `DestWac` | Destination Airport, World Area Code |
| 30 | `CRSDepTime` | CRS Departure Time (local time: hhmm) |
| 31 | `DepTime` | Actual Departure Time (local time: hhmm) |
| 32 | `DepDelay` | Difference in minutes between scheduled and actual departure time. Early departures show negative numbers. |
| 33 | `DepDelayMinutes` | Difference in minutes between scheduled and actual departure time. Early departures set to 0. |
| 34 | `DepDel15` | Departure Delay Indicator, 15 Minutes or More (1=Yes) |
| 35 | `DepartureDelayGroups` | Departure Delay intervals, every (15 minutes from 180) |
| 36 | `DepTimeBlk` | CRS Departure Time Block, Hourly Intervals |
| 37 | `TaxiOut` | Taxi Out Time, in Minutes |
| 38 | `WheelsOff` | Wheels Off Time (local time: hhmm) |
| 39 | `WheelsOn` | Wheels On Time (local time: hhmm) |
| 40 | `TaxiIn` | Taxi In Time, in Minutes |
| 41 | `CRSArrTime` | CRS Arrival Time (local time: hhmm) |
| 42 | `ArrTime` | Actual Arrival Time (local time: hhmm) |
| 43 | `ArrDelay` | Difference in minutes between scheduled and actual arrival time. Early arrivals show negative numbers. |
| 44 | `ArrDelayMinutes` | Difference in minutes between scheduled and actual arrival time. Early arrivals set to 0. |
| 45 | `ArrDel15` | Arrival Delay Indicator, 15 Minutes or More (1=Yes) |
| 46 | `ArrivalDelayGroups` | Arrival Delay intervals, every (15-minutes from 180) |
| 47 | `ArrTimeBlk` | CRS Arrival Time Block, Hourly Intervals |
| 48 | `Cancelled` | Cancelled Flight Indicator (1=Yes) |
| 49 | `CancellationCode` | Specifies The Reason For Cancellation |
| 50 | `Diverted` | Diverted Flight Indicator (1=Yes) |
| 51 | `CRSElapsedTime` | CRS Elapsed Time of Flight, in Minutes |
| 52 | `ActualElapsedTime` | Elapsed Time of Flight, in Minutes |
| 53 | `AirTime` | Flight Time, in Minutes |
| 54 | `Flights` | Number of Flights |
| 55 | `Distance` | Distance between airports (miles) |
| 56 | `DistanceGroup` | Distance Intervals, every 250 Miles, for Flight Segment |
| 57 | `CarrierDelay` | Carrier Delay, in Minutes |
| 58 | `WeatherDelay` | Weather Delay, in Minutes |
| 59 | `NASDelay` | National Air System Delay, in Minutes |
| 60 | `SecurityDelay` | Security Delay, in Minutes |
| 61 | `LateAircraftDelay` | Late Aircraft Delay, in Minutes |
| 62 | `FirstDepTime` | First Gate Departure Time at Origin Airport |
| 63 | `TotalAddGTime` | Total Ground Time Away from Gate for Gate Return or Cancelled Flight |
| 64 | `LongestAddGTime` | Longest Time Away from Gate for Gate Return or Cancelled Flight |
| 65 | `DivAirportLandings` | Number of Diverted Airport Landings |
| 66 | `DivReachedDest` | Diverted Flight Reaching Scheduled Destination Indicator (1=Yes) |
| 67 | `DivActualElapsedTime` | Elapsed Time of Diverted Flight Reaching Scheduled Destination, in Minutes. The ActualElapsedTime column remains NULL for all diverted flights. |
| 68 | `DivArrDelay` | Difference in minutes between scheduled and actual arrival time for a diverted flight reaching scheduled destination. The ArrDelay column remains NULL for all diverted flights. |
| 69 | `DivDistance` | Distance between scheduled destination and final diverted airport (miles). Value will be 0 for diverted flight reaching scheduled destination. |
| 70 | `Div1Airport` | Diverted Airport Code1 |
| 71 | `Div1AirportID` | Airport ID of Diverted Airport 1. Airport ID is a Unique Key for an Airport |
| 72 | `Div1AirportSeqID` | Airport Sequence ID of Diverted Airport 1. Unique Key for Time Specific Information for an Airport |
| 73 | `Div1WheelsOn` | Wheels On Time (local time: hhmm) at Diverted Airport Code1 |
| 74 | `Div1TotalGTime` | Total Ground Time Away from Gate at Diverted Airport Code1 |
| 75 | `Div1LongestGTime` | Longest Ground Time Away from Gate at Diverted Airport Code1 |
| 76 | `Div1WheelsOff` | Wheels Off Time (local time: hhmm) at Diverted Airport Code1 |
| 77 | `Div1TailNum` | Aircraft Tail Number for Diverted Airport Code1 |
| 78 | `Div2Airport` | Diverted Airport Code2 |
| 79 | `Div2AirportID` | Airport ID of Diverted Airport 2. Airport ID is a Unique Key for an Airport |
| 80 | `Div2AirportSeqID` | Airport Sequence ID of Diverted Airport 2. Unique Key for Time Specific Information for an Airport |
| 81 | `Div2WheelsOn` | Wheels On Time (local time: hhmm) at Diverted Airport Code2 |
| 82 | `Div2TotalGTime` | Total Ground Time Away from Gate at Diverted Airport Code2 |
| 83 | `Div2LongestGTime` | Longest Ground Time Away from Gate at Diverted Airport Code2 |
| 84 | `Div2WheelsOff` | Wheels Off Time (local time: hhmm) at Diverted Airport Code2 |
| 85 | `Div2TailNum` | Aircraft Tail Number for Diverted Airport Code2 |
| 86 | `Div3Airport` | Diverted Airport Code3 |
| 87 | `Div3AirportID` | Airport ID of Diverted Airport 3. Airport ID is a Unique Key for an Airport |
| 88 | `Div3AirportSeqID` | Airport Sequence ID of Diverted Airport 3. Unique Key for Time Specific Information for an Airport |
| 89 | `Div3WheelsOn` | Wheels On Time (local time: hhmm) at Diverted Airport Code3 |
| 90 | `Div3TotalGTime` | Total Ground Time Away from Gate at Diverted Airport Code3 |
| 91 | `Div3LongestGTime` | Longest Ground Time Away from Gate at Diverted Airport Code3 |
| 92 | `Div3WheelsOff` | Wheels Off Time (local time: hhmm) at Diverted Airport Code3 |
| 93 | `Div3TailNum` | Aircraft Tail Number for Diverted Airport Code3 |
| 94 | `Div4Airport` | Diverted Airport Code4 |
| 95 | `Div4AirportID` | Airport ID of Diverted Airport 4. Airport ID is a Unique Key for an Airport |
| 96 | `Div4AirportSeqID` | Airport Sequence ID of Diverted Airport 4. Unique Key for Time Specific Information for an Airport |
| 97 | `Div4WheelsOn` | Wheels On Time (local time: hhmm) at Diverted Airport Code4 |
| 98 | `Div4TotalGTime` | Total Ground Time Away from Gate at Diverted Airport Code4 |
| 99 | `Div4LongestGTime` | Longest Ground Time Away from Gate at Diverted Airport Code4 |
| 100 | `Div4WheelsOff` | Wheels Off Time (local time: hhmm) at Diverted Airport Code4 |
| 101 | `Div4TailNum` | Aircraft Tail Number for Diverted Airport Code4 |
| 102 | `Div5Airport` | Diverted Airport Code5 |
| 103 | `Div5AirportID` | Airport ID of Diverted Airport 5. Airport ID is a Unique Key for an Airport |
| 104 | `Div5AirportSeqID` | Airport Sequence ID of Diverted Airport 5. Unique Key for Time Specific Information for an Airport |
| 105 | `Div5WheelsOn` | Wheels On Time (local time: hhmm) at Diverted Airport Code5 |
| 106 | `Div5TotalGTime` | Total Ground Time Away from Gate at Diverted Airport Code5 |
| 107 | `Div5LongestGTime` | Longest Ground Time Away from Gate at Diverted Airport Code5 |
| 108 | `Div5WheelsOff` | Wheels Off Time (local time: hhmm) at Diverted Airport Code5 |
| 109 | `Div5TailNum` | Aircraft Tail Number for Diverted Airport Code5 |
