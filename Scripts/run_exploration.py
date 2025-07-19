from explore_data import run_exploration

# Run EDA on raw data
print("\n RAW DATA EXPLORATION")
run_exploration('input/netflix_titles.csv', 'output/plots/raw_data')

# Run EDA on cleaned data
print("\n CLEANED DATA EXPLORATION")
run_exploration('output/cleaned_netflix.csv', 'output/plots/cleaned_data')