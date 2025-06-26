
import pandas as pd
from utils import clean_netflix_data
import logging

logging.basicConfig(filename='logs/automation_log.txt', level=logging.INFO)

try:
    df = pd.read_csv('input/netflix_titles.csv')
    df = clean_netflix_data(df)
    df.to_csv('output/cleaned_netflix.csv', index=False)
    logging.info("Data cleaned and saved successfully.")
    print("Data cleaned and saved to output/cleaned_netflix.csv")
except Exception as e:
    logging.error("Error during data cleaning: %s", e)
    print(f"Error occurred: {e}")
