
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ---------------- PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="Airbnb Analytics Dashboard",
    page_icon="🏡",
    layout="wide"
)

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    path = Path(__file__).parent / "airbnbdata.csv"
    df = pd.read_csv(path)

    df["price"] = pd.to_numeric(
        df["price"].astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False),
        errors="coerce"
    )

    for col in ["room_type", "neighbourhood"]:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown")

    return df


try:
    df = load_data()
except Exception as e:
    st.error(f"Could not load dataset: {e}")
    st.stop()

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.title("Dashboard Filters")

if "room_type" not in df.columns or "neighbourhood" not in df.columns:
    st.error("Dataset must contain room_type and neighbourhood columns.")
    st.stop()

rooms = st.sidebar.multiselect(
    "Room Type",
    sorted(df["room_type"].unique()),
    default=sorted(df["room_type"].unique())
)

areas = st.sidebar.multiselect(
    "Neighbourhood",
    sorted(df["neighbourhood"].unique()),
    default=sorted(df["neighbourhood"].unique())
)

filtered = df[
    df["room_type"].isin(rooms)
    & df["neighbourhood"].isin(areas)
].copy()

valid = filtered[
    filtered["price"].notna() & (filtered["price"] > 0)
].copy()

# ---------------- DASHBOARD HEADER ----------------
st.title("🏡 Airbnb Analytics Dashboard")
st.markdown(
    "Explore listing prices, room types and neighbourhood trends."
)
st.caption("Built with Python | Pandas | Plotly | Streamlit")

# ---------------- KPI CARDS ----------------
c1, c2, c3, c4 = st.columns(4)

kpis = [
    ("TOTAL LISTINGS", f"{len(filtered):,}", "All Airbnb listings"),
    ("ROOM TYPES", str(filtered["room_type"].nunique()), "Accommodation types"),
    ("NEIGHBOURHOODS", str(filtered["neighbourhood"].nunique()), "Areas covered"),
    (
        "MEDIAN PRICE",
        f"{valid['price'].median():,.2f}" if not valid.empty else "N/A",
        "Typical listing price"
    )
]

for col, (label, value, subtitle) in zip([c1, c2, c3, c4], kpis):
    with col:
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #172554, #1e40af);
                padding: 22px 16px;
                border-radius: 14px;
                border: 1px solid #3b82f6;
                min-height: 130px;
                margin-bottom: 15px;
            ">
                <div style="color:#bfdbfe; font-size:13px;
                            font-weight:600; letter-spacing:1px;">
                    {label}
                </div>
                <div style="color:white; font-size:30px;
                            font-weight:700; margin-top:12px;">
                    {value}
                </div>
                <div style="color:#dbeafe; font-size:12px;
                            margin-top:6px;">
                    {subtitle}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

st.divider()

# ---------------- CHART 1 ----------------
st.subheader("1. Price Comparison Across Room Types")

if not valid.empty:
    room_prices = (
        valid.groupby("room_type", as_index=False)["price"]
        .median()
        .sort_values("price", ascending=False)
    )

    fig1 = px.bar(
        room_prices,
        x="room_type",
        y="price",
        color="room_type",
        text_auto=".2f",
        title="Median Price by Room Type",
        template="plotly_white",
        labels={
            "room_type": "Room Type",
            "price": "Median Price"
        }
    )
    fig1.update_layout(showlegend=False)
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.info("No valid prices available for the selected filters.")

st.divider()

# ---------------- CHART 2 ----------------
st.subheader("2. Hotel Room Price Across Neighbourhoods")

hotel = valid[
    valid["room_type"].str.strip().str.lower() == "hotel room"
]

if not hotel.empty:
    hotel_prices = (
        hotel.groupby("neighbourhood", as_index=False)["price"]
        .median()
        .sort_values("price", ascending=False)
    )

    fig2 = px.bar(
        hotel_prices,
        x="neighbourhood",
        y="price",
        color="price",
        text_auto=".2f",
        title="Median Hotel Room Price by Neighbourhood",
        template="plotly_white",
        labels={
            "neighbourhood": "Neighbourhood",
            "price": "Median Price"
        }
    )
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("No hotel-room listings match these filters.")

st.divider()

# ---------------- CHART 3 ----------------
st.subheader("3. Number of Listings Across Neighbourhoods")

if not filtered.empty:
    counts = (
        filtered.groupby("neighbourhood")
        .size()
        .reset_index(name="Listings")
        .sort_values("Listings", ascending=False)
        .head(10)
        .sort_values("Listings")
    )

    fig3 = px.bar(
        counts,
        x="Listings",
        y="neighbourhood",
        orientation="h",
        text="Listings",
        title="Top 10 Neighbourhoods by Listings",
        template="plotly_white",
        labels={
            "Listings": "Number of Listings",
            "neighbourhood": "Neighbourhood"
        }
    )
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("No listings available for the selected filters.")

st.divider()


# ---------------- GAPMINDER LINE CHART ----------------
st.subheader("4. Life Expectancy Trend — Australia & New Zealand")

# Load Plotly's built-in Gapminder dataset
df_gapminder = px.data.gapminder()

# Filter only Oceania countries
df_oceania = df_gapminder.query('continent == "Oceania"')

# Create line chart
fig5 = px.line(
    df_oceania,
    x="year",
    y="lifeExp",
    color="country",
    markers=True,
    title="Life Expectancy Over the Years",
    labels={
        "year": "Year",
        "lifeExp": "Life Expectancy (Years)",
        "country": "Country"
    },
    template="plotly_white"
)

# Show markers and connecting lines
fig5.update_traces(mode="markers+lines")

fig5.update_layout(
    hovermode="x unified",
    legend_title_text="Country"
)

st.plotly_chart(fig5, use_container_width=True)

st.caption(
    "Source: Plotly Gapminder sample dataset. "
    "This chart is separate from the Airbnb dataset."
)

st.divider()


# ---------------- CHART 4: YEAR-WISE PRICE TREND ----------------
st.subheader("5. Airbnb Price Trend Over Years")

if "last_review" in filtered.columns and not valid.empty:

    trend_data = valid.copy()

    trend_data["last_review"] = pd.to_datetime(
        trend_data["last_review"], errors="coerce"
    )

    trend_data = trend_data.dropna(subset=["last_review"])

    if not trend_data.empty:

        trend_data["year"] = trend_data["last_review"].dt.year

        yearly_prices = (
            trend_data.groupby("year", as_index=False)["price"]
            .median()
            .sort_values("year")
        )

        fig4 = px.line(
            yearly_prices,
            x="year",
            y="price",
            markers=True,
            title="Year-wise Median Airbnb Price",
            labels={
                "year": "Year",
                "price": "Median Price"
            },
            template="plotly_white"
        )

        fig4.update_traces(mode="markers+lines")

        fig4.update_layout(
            xaxis_title="Year",
            yaxis_title="Median Price",
            hovermode="x unified"
        )

        st.plotly_chart(fig4, use_container_width=True)

    else:
        st.info("No valid review dates found in the selected data.")

else:
    st.info(
        "The dataset must contain a last_review column "
        "to display the year-wise price trend."
    )

st.divider()


# ---------------- GEOGRAPHICAL MAP ----------------
st.subheader("6. Geographical Distribution of Airbnb Listings")
st.caption(
    "Explore listing locations, prices and room types on the map."
)

required_columns = {"latitude", "longitude", "price"}

if required_columns.issubset(filtered.columns):

    map_data = filtered.copy()

    for col in ["latitude", "longitude", "price"]:
        map_data[col] = pd.to_numeric(
            map_data[col], errors="coerce"
        )

    map_data = map_data.dropna(
        subset=["latitude", "longitude", "price"]
    )

    map_data = map_data[
        map_data["latitude"].between(-90, 90)
        & map_data["longitude"].between(-180, 180)
        & (map_data["price"] > 0)
    ].copy()

    if not map_data.empty:

        hover_columns = [
            col for col in ["price", "room_type", "neighbourhood"]
            if col in map_data.columns
        ]

        #map_arguments = {
           # "data_frame": map_data,
           # "lat": "latitude",
           # "lon": "longitude",
           # "color": "room_type",
            #"size": "price",
            #"size_max": 15,
          #  "hover_data": hover_columns,
          #  "zoom": 9,
           # "height": 550,
           # "map_style": "open-street-map",
           ## "title": "Airbnb Listings by Geographic Location"
       # }
        map_arguments = {
    "data_frame": map_data,
    "lat": "latitude",
    "lon": "longitude",
    "color": "room_type",
    "size": "price",
    "size_max": 15,
    "hover_data": hover_columns,
    "zoom": 9,
    "height": 550,
    "map_style": "open-street-map",
    "title": "Airbnb Listings by Geographic Location"
}
        map_fig = px.scatter_map(**map_arguments)

        if "name" in map_data.columns:
            map_arguments["hover_name"] = "name"
            
        map_fig = px.scatter_map(**map_arguments)

        map_fig.update_layout(
            margin=dict(l=0, r=0, t=50, b=0),
            legend_title_text="Room Type"
        )

        st.plotly_chart(
            map_fig,
            use_container_width=True
        )

        st.caption(
            f"Displaying {len(map_data):,} listings with valid coordinates and prices."
        )

    else:
        st.warning(
            "No valid geographical coordinates and prices found "
            "for the selected filters."
        )

else:
    st.warning(
        "Latitude, longitude and price columns are required for the map."
    )

st.divider()

# ---------------- DATASET PREVIEW ----------------
with st.expander("Explore Dataset"):
    st.write(f"Showing {len(filtered):,} filtered listings.")
    st.dataframe(filtered, use_container_width=True)

    csv_data = filtered.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Filtered Data as CSV",
        data=csv_data,
        file_name="filtered_airbnb.csv",
        mime="text/csv"
    )

# ---------------- FOOTER ----------------
st.divider()
st.caption(
    "Airbnb Analytics Portfolio | Built with Python, Pandas, Plotly and Streamlit"
)


