import pandas as pd
import logging
from textblob import TextBlob


# Data Cleaning
def clean_netflix_data(df):
    # Standardize and parse 'date_added' column with expected format
    try:
        df['date_added'] = pd.to_datetime(
            df['date_added'].astype(str).str.strip(),
            format="%B %d, %Y",
            errors='coerce'
        )
    except Exception as e:
        logging.warning(f"Date parsing failed: {e}")

    invalid_date_count = df['date_added'].isna().sum()
    df['year_added'] = df['date_added'].dt.year
    df['month_added'] = df['date_added'].dt.month

    missing_country_count = df['country'].isna().sum()
    df['country'] = df['country'].fillna('Unknown')
    df['country'] = df['country'].apply(lambda x: str(x).split(',')[0].strip())

    df['rating'] = df['rating'].fillna('Unknown')
    df['duration'] = df['duration'].fillna('Unknown')
    df['director'] = df['director'].fillna('Unknown')
    df['cast'] = df['cast'].fillna('Unknown')
    df['description'] = df['description'].astype(str).fillna('').str.strip()
    df['primary_genre'] = df['listed_in'].apply(
        lambda x: str(x).split(',')[0].strip() if isinstance(x, str) else 'Unknown'
    )

    logging.info(f"Filled {missing_country_count} missing countries with 'Unknown'")
    logging.info(f"Removed {invalid_date_count} invalid or malformed 'date_added' entries")

    return df

# Sentiment Analysis
def add_sentiment_columns(df):
    df['description_tone'] = df['description'].apply(lambda x: TextBlob(str(x)).sentiment.polarity)

    def get_sentiment_label(polarity):
        if polarity > 0:
            return 'Positive'
        elif polarity < 0:
            return 'Negative'
        else:
            return 'Neutral'

    df['sentiment_label'] = df['description_tone'].apply(get_sentiment_label)
    return df

# Utility Functions
def get_top_genres(df):
    return df['primary_genre'].value_counts().head(10)

def get_top_ratings(df):
    return df['rating'].value_counts().head(10)

def get_content_type_distribution(df):
    return df['type'].value_counts()
