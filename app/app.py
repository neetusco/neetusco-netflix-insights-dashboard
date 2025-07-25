import streamlit as st  
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import plotly.express as px
import logging
import sys, os
from sqlalchemy import create_engine
from urllib.parse import quote_plus


# ---------------- Custom Authentication Setup ----------------

def login():
    st.header("Login")
    role = st.selectbox("Select Role", ["Admin User", "Data Analyst"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_btn = st.button("Login")
    if login_btn:
        # Map role to username and password
        credentials = {
            "Admin User": {"username": "admin", "password": "admin123"},
            "Data Analyst": {"username": "analyst", "password": "netflix2024"}
        }
        expected = credentials[role]
        if username == expected["username"] and password == expected["password"]:
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.session_state["role"] = role
        else:
            st.session_state["authenticated"] = False
            st.error("Invalid username or password.")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "role" not in st.session_state:
    st.session_state["role"] = ""

if not st.session_state["authenticated"]:
    login()
    st.stop()
else:
    st.success(f"Welcome, {st.session_state['username']}! Role: {st.session_state['role']}")
    st_autorefresh(interval=60000, limit=None, key="auto_refresh")  # Auto-refresh every 60 seconds
    import datetime
    st.info(f"Last update: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
# ---------------- Setup ----------------
st.set_page_config(layout="wide")
st.title("Netflix Insights Dashboard: Content Analysis & Description Sentiment")

logging.basicConfig(filename='logs/app_log.txt', level=logging.INFO)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Scripts.data_preparation import get_top_genres, get_top_ratings, get_content_type_distribution

# ---------------- SQLAlchemy Engine ----------------
@st.cache_resource
def get_engine():
    driver = quote_plus("ODBC Driver 17 for SQL Server")
    conn_str = f"mssql+pyodbc://@NEETIKA/CollegeProjectDB?driver={driver}&trusted_connection=yes"
    return create_engine(conn_str)

# ---------------- Load Data ----------------
@st.cache_data
def load_data():
    engine = get_engine()
    df = pd.read_sql("SELECT * FROM CleanedNetflixData", con=engine)
    return df

@st.cache_data
def load_country_coordinates():
    engine = get_engine()
    coords_df = pd.read_sql("SELECT * FROM CountryCoordinates", con=engine)
    return coords_df.set_index('country')[['lat', 'lon']]

df = load_data()
country_coords = load_country_coordinates()

# ---------------- Sidebar Filters ----------------
st.sidebar.header("Filter Options")

default_type = df['type'].unique().tolist()
default_genre = df['primary_genre'].unique().tolist()
default_country = df['country'].unique().tolist()
default_sentiments = df['sentiment_label'].unique().tolist()

if 'reset' not in st.session_state:
    st.session_state.reset = False

if st.sidebar.button("Reset Filters"):
    st.session_state.reset = True
    st.rerun()

# --- Filters ---
st.sidebar.markdown("### Select Content Type")
select_all_type = st.sidebar.checkbox("Select All Content Types", value=True)
selected_type = st.sidebar.multiselect("Choose types:", default_type, default=default_type if select_all_type else [])

st.sidebar.markdown("### Select Genre")
select_all_genre = st.sidebar.checkbox("Select All Genres", value=True)
selected_genres = st.sidebar.multiselect("Choose genres:", default_genre, default=default_genre if select_all_genre else [])

st.sidebar.markdown("### Select Country")
select_all_country = st.sidebar.checkbox("Select All Countries", value=True)
selected_country = st.sidebar.multiselect("Choose countries:", default_country, default=default_country if select_all_country else [])

description_tone_range = st.sidebar.slider("Filter by Description Tone (Polarity Score):", -1.0, 1.0, (-1.0, 1.0))

st.sidebar.markdown("### Sentiment Category")
select_all_sentiments = st.sidebar.checkbox("Select All Sentiments", value=True)
selected_sentiments = st.sidebar.multiselect("Choose sentiments:", default_sentiments, default=default_sentiments if select_all_sentiments else [])

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
    (df['description_tone'].between(description_tone_range[0], description_tone_range[1])) &
    (df['sentiment_label'].isin(selected_sentiments))
]

# ---------------- Display Filtered Data ----------------
st.subheader("Filtered Dataset Preview")
if not filtered_df.empty:
    st.dataframe(filtered_df[['title', 'type', 'primary_genre', 'country', 'rating', 'description_tone', 'sentiment_label']].sample(min(10, len(filtered_df))))
else:
    st.warning("No data matches the selected filters.")

# ---------------- Dynamic Charts ----------------
if not filtered_df.empty:



    # ---------------- Country Map ----------------
    st.subheader("Country-wise Content Distribution")
    country_counts = filtered_df[filtered_df['country'] != 'Unknown']['country'].value_counts().reset_index()
    country_counts.columns = ['country', 'count']
    country_counts = country_counts.merge(country_coords, how='left', left_on='country', right_index=True)
    country_counts.dropna(subset=['lat', 'lon'], inplace=True)

    fig = px.scatter_geo(
        country_counts,
        lat='lat',
        lon='lon',
        size='count',
        color='count',
        hover_name='country',
        projection='natural earth',
        title='Netflix Titles by Country',
        template='plotly_white',
        width=1200,
        height=700
    )

    fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
    st.plotly_chart(fig, use_container_width=False)

    st.subheader("Avg Description Tone by Genre")
    genre_sentiment = filtered_df.groupby('primary_genre')['description_tone'].mean().sort_values()
    st.bar_chart(genre_sentiment)

    st.subheader("Avg Description Tone by Content Type")
    type_sentiment = filtered_df.groupby('type')['description_tone'].mean().sort_values()
    st.bar_chart(type_sentiment)



    st.subheader("Avg Description Tone by Country")
    country_sentiment = filtered_df.groupby('country')['description_tone'].mean().sort_values()
    st.bar_chart(country_sentiment)

    # Download Filtered Data
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Filtered Data", csv, "filtered_netflix.csv", "text/csv")

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
