# Netflix Insights Streamlit App
This Streamlit application allows users to explore and analyze Netflix content based on genre, country, and description tone.

## Features
- Filterable views by content type, genre, country, and tone polarity
- Sentiment analysis of description texts using TextBlob
- Country-wise content distribution on interactive map
- Pie and bar charts for content type, top genres, and ratings
- Download filtered dataset
- Reset and select-all options for filters
- Insight summary section

## Folder Structure
```
├── app/
│   └── app.py               # Main Streamlit application
├── input/
│   └── country_coordinates.csv
├── output/
│   └── cleaned_netflix.csv
├── logs/
│   └── app_log.txt
├── visuals/
├── requirements.txt
├── README.md
```

## How to Run Locally
```bash
pip install -r requirements.txt
streamlit run app/app.py
```

## Deploy to Streamlit Cloud
1. Push this repository to GitHub
2. Go to https://streamlit.io/cloud
3. Connect your GitHub & select the repo
4. Make sure to set the main file path to `app/app.py`

Enjoy exploring Netflix data!