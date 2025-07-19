import pandas as pd
import logging
import os
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from data_preparation import clean_netflix_data, add_sentiment_columns

# ------------------------ Logging Setup ------------------------
os.makedirs('logs', exist_ok=True)
logging.basicConfig(filename='logs/cleaning_log.txt', level=logging.INFO)

# ------------------------ Database Connection ------------------------
def get_sqlalchemy_engine(server, database):
    driver = quote_plus("ODBC Driver 17 for SQL Server")
    connection_string = (
        f"mssql+pyodbc://@NEETIKA/CollegeProjectDB?driver={driver}&trusted_connection=yes"
    )
    return create_engine(connection_string)

# ------------------------ Main Orchestration ------------------------
def prepare_and_store_data(
    input_path='input/netflix_titles.csv',
    coords_path='input/country_coordinates.csv',
    output_path='output/cleaned_netflix.csv',
    server='NEETIKA',
    database='CollegeProjectDB',
    table_name='CleanedNetflixData',
    coords_table='CountryCoordinates'
):
    try:
        # Load raw CSV
        df = pd.read_csv(input_path)
        logging.info(" Raw data loaded.")

        # Clean + add sentiment
        df = clean_netflix_data(df)
        df = add_sentiment_columns(df)
        logging.info("Data cleaned and sentiment added.")

        # Save locally
        os.makedirs('output', exist_ok=True)
        df.to_csv(output_path, index=False)
        logging.info(f"Cleaned data saved locally to {output_path}")

        # Save to SQL Server using SQLAlchemy
        engine = get_sqlalchemy_engine(server, database)
        df.to_sql(table_name, con=engine, index=False, if_exists='replace')
        logging.info(f"Data saved to SQL Server table '{table_name}' in database '{database}'.")
        
        # Load and save country coordinates
        coord_df = pd.read_csv(coords_path)
        coord_df.to_sql(coords_table, con=engine, index=False, if_exists='replace')
        logging.info(f"Country coordinates saved to SQL table '{coords_table}'.")

        print(f" Both datasets successfully saved to SQL Server: '{table_name}' and '{coords_table}'.")
        
    except Exception as e:
        logging.error(f"Pipeline failed: {e}")
        print(f"Error occurred: {e}")

# ------------------------ Execute ------------------------
if __name__ == "__main__":
    prepare_and_store_data(
        server='NEETIKA',
        database='CollegeProjectDB'
    )