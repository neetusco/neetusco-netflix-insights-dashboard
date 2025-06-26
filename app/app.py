import streamlit as st
import pandas as pd
import pydeck as pdk
import logging
from utils import get_top_genres, get_top_ratings, get_content_type_distribution

st.set_page_config(layout="wide")
st.title("Netflix Insights Dashboard: Content Analysis & Description Sentiment")

logging.basicConfig(filename='logs/app_log.txt', level=logging.INFO)

# ---------------- Load Data ----------------
@st.cache_data
def load_data():
    df = pd.read_csv("output/cleaned_netflix.csv")

    # Log missing and invalid values
    missing_country_count = df['country'].isna().sum()
    logging.info(f"Found {missing_country_count} missing 'country' values in app preview load.")

    original_date_count = df['date_added'].notna().sum()
    df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
    cleaned_date_count = df['date_added'].notna().sum()
    invalid_date_count = original_date_count - cleaned_date_count
    logging.info(f"Detected {invalid_date_count} invalid 'date_added' entries in app preview load.")

    return df

@st.cache_data
def load_country_coordinates():
    coords_df = pd.read_csv("input/country_coordinates.csv")
    return coords_df.set_index('country')[['lat', 'lon']]

df = load_data()
country_coords = load_country_coordinates()

# ---------------- Sidebar Filters with Reset ----------------
st.sidebar.header("Filter Options")

# Defaults
default_type = df['type'].unique().tolist()
default_genre = df['primary_genre'].unique().tolist()
default_country = df['country'].unique().tolist()

# Session state
if 'reset' not in st.session_state:
    st.session_state.reset = False

if st.sidebar.button("Reset Filters"):
    st.session_state.reset = True
    st.rerun()

# --- Content Type ---
st.sidebar.markdown("### Select Content Type")
select_all_type = st.sidebar.checkbox("Select All Content Types", value=True)
selected_type = st.sidebar.multiselect("Choose types:", default_type, default=default_type if select_all_type else [])

# --- Genre ---
st.sidebar.markdown("### Select Genre")
select_all_genre = st.sidebar.checkbox("Select All Genres", value=True)
selected_genres = st.sidebar.multiselect("Choose genres:", default_genre, default=default_genre if select_all_genre else [])

# --- Country ---
st.sidebar.markdown("### Select Country")
select_all_country = st.sidebar.checkbox("Select All Countries", value=True)
selected_country = st.sidebar.multiselect("Choose countries:", default_country, default=default_country if select_all_country else [])

# --- Description Tone Range ---
description_tone_range = st.sidebar.slider("Filter by Description Tone (Polarity Score):", -1.0, 1.0, (-1.0, 1.0))

# ---------------- Static Summary Charts ----------------
st.subheader("Netflix Content Overview (All Data)")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Top 10 Genres**")
    st.bar_chart(get_top_genres(df))

    st.markdown("**Top Ratings**")
    st.bar_chart(get_top_ratings(df))

with col2:
    st.markdown("<h4 style='text-align: center;'>Content Type Distribution</h4>", unsafe_allow_html=True)
    type_counts = get_content_type_distribution(df)
    st.pyplot(type_counts.plot.pie(autopct='%1.1f%%', figsize=(5, 5), ylabel='').figure)

# ---------------- Apply Filters ----------------
filtered_df = df[
    (df['type'].isin(selected_type)) &
    (df['primary_genre'].isin(selected_genres)) &
    (df['country'].isin(selected_country)) &
    (df['description_tone'].between(description_tone_range[0], description_tone_range[1]))
]

# ---------------- Display Filtered Data ----------------
st.subheader("Filtered Dataset Preview")
if not filtered_df.empty:
    st.dataframe(filtered_df[['title', 'type', 'primary_genre', 'country', 'rating', 'description_tone']].sample(min(10, len(filtered_df))))
else:
    st.warning("No data matches the selected filters.")

# ---------------- Dynamic Charts ----------------
if not filtered_df.empty:
    st.subheader("Avg Description Tone by Genre (Filtered)")
    genre_sentiment = filtered_df.groupby('primary_genre')['description_tone'].mean().sort_values()
    st.bar_chart(genre_sentiment)

    st.subheader("Avg Description Tone by Content Type (Filtered)")
    type_sentiment = filtered_df.groupby('type')['description_tone'].mean().sort_values()
    st.bar_chart(type_sentiment)

    # Download Filtered Data
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Filtered Data", csv, "filtered_netflix.csv", "text/csv")

    # ---------------- Country Map ----------------
    st.subheader("Country-wise Content Distribution")
    country_counts = filtered_df['country'].value_counts().reset_index()
    country_counts.columns = ['country', 'count']
    country_counts = country_counts.merge(country_coords, how='left', left_on='country', right_index=True)
    country_counts.dropna(subset=['lat', 'lon'], inplace=True)

    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(latitude=20, longitude=0, zoom=1, pitch=0),
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=country_counts,
                get_position='[lon, lat]',
                get_radius='50000 + count * 200',
                get_fill_color='[200, 30, 0, 160]',
                pickable=True
            )
        ]
    ))

# ---------------- Insight Summary ----------------
st.subheader("Insight Summary")
with st.expander("Click to view insights"):
    st.markdown("""
    - **Movies dominate** the platform, but TV Shows are gaining ground.
    - **Drama** is the most represented genre across the catalog.
    - **Content description tone** is mostly neutral to slightly positive.
    - **Countries like the United States, India, and the UK** have the highest content contributions.
    - Consider improving content discoverability by aligning tone with genre (e.g., upbeat tone in comedies).
    """)

st.success("Use this app to explore how Netflix describes its content and how tone varies across genres, formats, and countries.")
