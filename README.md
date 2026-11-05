# Storms and Flight Delays: Weather Impact Analysis App

This project measures how thunderstorms and hail change US flight delays. With my teammate Joshua Bajowa, I joined 607,577 domestic flights from June 2026 with NOAA lightning and hail radar data, giving 9,416 airport-days at 320 airports. We then built an interactive Streamlit app that answers seven questions with charts. The app also has an AI "Vis Agent" that answers a user's own question with a chart.

| Question | Finding |
|---|---|
| 1. Does lightning at an airport increase delays? | Mean departure delay rises from 16.6 minutes on days with no lightning to 57.0 minutes with more than 50 strikes |
| 2. Which places lose the most time to storms? | Texas hubs: DFW loses about 49 extra minutes on a lightning day. Florida has the most storm days but loses a median of only 5.5 minutes |
| 3. Does the official "weather delay" match the radar? | 73% of airport-days with a reported weather delay had no storm in the airport's grid cell |
| 4. Which delay cause grows most on storm days? | On lightning-and-hail days, late aircraft add 7.9 minutes per flight and weather adds 5.7 |
| 5. Do hail and lightning act differently? | Alone, each cancels about 2% of flights. Together, they cancel about 6%, five times a clear day |
| 6. Do storms elsewhere delay dry airports? | Yes. Late-aircraft delay at dry airports rises from 5.9 to 9.8 minutes per flight when lightning is heavy across the country |
| 7. Which airlines handle storms best? | At the same airports, a storm day costs SkyWest 8.7 extra minutes and PSA 22.5 (average 14.4) |

## Topics Covered

- Joining three data sources on a 0.1-degree latitude and longitude grid
- Data cleaning: time zones (UTC weather days and local flight dates), missing values and skewed delays
- Aggregating flights to one row per airport per day
- Exploratory analysis and interactive charts with selections, highlights and tooltips
- Building a multi-page Streamlit app
- Deploying with Docker on Google Cloud Run, with the data in Cloud Storage
- An LLM agent that picks a dataset, writes chart code, tests it and reviews the result
- User studies and an evaluation of the agent across repeated runs

## Python Libraries Used

- `pandas` and `NumPy`: cleaning, joining and aggregating the data
- `altair`: interactive charts
- `streamlit`: the web app
- `gcsfs`: reading the data from Google Cloud Storage
- `openai`: calling Gemini through its OpenAI-compatible API, for the Vis Agent
- `pydantic`: checking the arguments of the agent's tool calls
- `logfire`: tracing the agent's calls

Files:
- `milestone0/`: Dataset choice and the first data card
- `milestone1/load-prep-data.ipynb`: Loading, cleaning and joining the data
- `milestone2/vis-analysis.ipynb`: The seven questions, with draft and refined charts
- `milestone3/streamlit/`: The first version of the app, one page per question
- `milestone4/streamlit/`: The final app with the Vis Agent (`vis_agent.py`)
- `milestone4/data-card.pdf`: The final report: data sources, cleaning, findings and evaluations
- `datasets/`: Data dictionaries only. The raw CSV files are too large for GitHub, and the data card lists where to download them
