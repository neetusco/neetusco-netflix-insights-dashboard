# Modules/explore_data.py

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def print_eda_summary(df):
    print("Dataset Summary")
    print("-" * 40)
    print("Shape:", df.shape)
    print("\nColumns:", df.columns.tolist())
    print("\nData Types:\n", df.dtypes)
    print("\nMissing Values:\n", df.isna().sum())
    
    if 'type' in df.columns:
        print("\nContent Type Distribution:\n", df['type'].value_counts(normalize=True) * 100)
    
    if 'country' in df.columns:
        print("\nTop 10 Countries:\n", df['country'].value_counts().head(10))

    if 'listed_in' in df.columns:
        print("\nTop 10 Genre Combinations:\n", df['listed_in'].value_counts().head(10))

    if 'release_year' in df.columns:
        release_year_counts = df['release_year'].value_counts().sort_index()
        print("\nContent Releases Over Time (Recent):\n", release_year_counts.tail(10))

    if 'rating' in df.columns:
        print("\nTop Content Ratings:\n", df['rating'].value_counts().head(10))

    if 'description' in df.columns:
        print("\nSample Descriptions:\n", df['description'].dropna().sample(3).tolist())

    if 'date_added' in df.columns:
        print("\nSample 'date_added' Values:\n", df['date_added'].dropna().sample(3))

    print("\nDuplicate Rows:", df.duplicated().sum())
    print("-" * 40)

def generate_visualizations(df, output_dir='output/plots'):
    os.makedirs(output_dir, exist_ok=True)
    sns.set(style="whitegrid")

    if 'type' in df.columns:
        plt.figure(figsize=(6, 6))
        df['type'].value_counts().plot.pie(autopct='%1.1f%%', startangle=90, colors=sns.color_palette("pastel"))
        plt.ylabel('')
        plt.title('Content Type Distribution')
        plt.savefig(f"{output_dir}/content_type_distribution.png")
        plt.close()

    if 'country' in df.columns:
        top_countries = df['country'].value_counts().head(10)
        plt.figure(figsize=(10, 6))
        sns.barplot(x=top_countries.values, y=top_countries.index, palette="Blues_d")
        plt.title("Top 10 Countries by Content Count")
        plt.xlabel("Number of Titles")
        plt.savefig(f"{output_dir}/top_countries.png")
        plt.close()

    if 'listed_in' in df.columns:
        top_genres = df['listed_in'].value_counts().head(10)
        plt.figure(figsize=(10, 6))
        sns.barplot(x=top_genres.values, y=top_genres.index, palette="Greens_d")
        plt.title("Top 10 Genre Combinations")
        plt.xlabel("Number of Titles")
        plt.savefig(f"{output_dir}/top_genres.png")
        plt.close()

    if 'release_year' in df.columns:
        release_year_counts = df['release_year'].value_counts().sort_index()
        plt.figure(figsize=(12, 6))
        sns.lineplot(x=release_year_counts.index, y=release_year_counts.values, marker="o")
        plt.title("Content Releases Over Years")
        plt.xlabel("Year")
        plt.ylabel("Number of Releases")
        plt.savefig(f"{output_dir}/content_releases_over_time.png")
        plt.close()

    if 'rating' in df.columns:
        top_ratings = df['rating'].value_counts().head(10)
        plt.figure(figsize=(10, 6))
        sns.barplot(x=top_ratings.values, y=top_ratings.index, palette="Reds_d")
        plt.title("Top Content Ratings")
        plt.xlabel("Number of Titles")
        plt.savefig(f"{output_dir}/top_ratings.png")
        plt.close()

    print(f"Visualizations saved in '{output_dir}'")

def run_exploration(file_path='input/netflix_titles.csv', output_dir='output/plots'):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    
    try:
        df = pd.read_csv(file_path)
        print(f"\n Loaded dataset: {file_path}")
        print_eda_summary(df)
        generate_visualizations(df, output_dir)
    except Exception as e:
        print(f"Failed to run EDA: {e}")
