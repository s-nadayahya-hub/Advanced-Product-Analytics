import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import numpy as np
import math
import re
import time
from serpapi.google_search import GoogleSearch
from PIL import Image
import requests

# -----------------------
# Page Config
# -----------------------
st.set_page_config(page_title="Advanced Product Pro", layout="wide")

# -----------------------
# Header Image
# -----------------------
img = Image.open("cover.jpeg")
img = img.resize((1200, 400))
st.image(img, use_container_width=True)

# -----------------------
# CSS
# -----------------------
st.markdown("""
<style>
.stApp { background-color: #FFFFFF; }
.card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

st.title("🚀 Advanced Product Analytics Pro")
st.markdown("---")

# -----------------------
# API Function
# -----------------------
@st.cache_data
def api_search_products(product_name):

    params = {
        "engine": "google_shopping",
        "q": product_name,
        "api_key": "YOUR_SERPAPI_KEY"   # ⚠️ مهم تغيريه لو عايزة online mode
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    products = results.get("shopping_results", [])

    data = []

    for item in products:
        price = item.get("price", "0")
        if isinstance(price, str):
            price = re.sub(r"[^\d.]", "", price)
            price = float(price) if price else 0

        data.append({
            "Title": item.get("title", "No Title"),
            "Price": price,
            "Rating": item.get("rating", 0),
            "Store": item.get("source", "Unknown"),
            "Link": item.get("product_link", ""),
            "Reviews": item.get("reviews", 0),
        })

    df = pd.DataFrame(data)

    df["Positive Feedback %"] = df["Rating"].fillna(0) * 20

    return df.dropna()


# -----------------------
# Load Data
# -----------------------
st.sidebar.title("DATA SOURCE")

data_source = st.sidebar.radio(
    "Choose Data Source",
    ["CSV File", "Online Scraping"]
)

if data_source == "CSV File":
    df = pd.read_csv("amazon_lip_gloss.csv")   # ✅ fixed

else:
    keyword = st.sidebar.text_input("Enter Product Keyword")

    if keyword:
        with st.spinner("Scraping..."):
            df = api_search_products(keyword)
    else:
        st.warning("Enter keyword")
        st.stop()

# -----------------------
# Clean Data
# -----------------------
df["Price"] = pd.to_numeric(df["Price"], errors="coerce").fillna(0)
df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce").fillna(0)
df["Reviews"] = pd.to_numeric(df["Reviews"], errors="coerce").fillna(0)

df["Value"] = df["Rating"] / (df["Price"].replace(0, 1))

# -----------------------
# Sidebar Image
# -----------------------
st.sidebar.image("sidebar.png", width=120)

# -----------------------
# Filters
# -----------------------
price_range = st.sidebar.slider(
    "Price Range",
    float(df["Price"].min()),
    float(df["Price"].max()),
    (float(df["Price"].min()), float(df["Price"].max()))
)

filtered_df = df[df["Price"].between(*price_range)]

if filtered_df.empty:
    st.warning("No data found")
    st.stop()

# -----------------------
# Best Picks
# -----------------------
best_price = filtered_df.loc[filtered_df["Price"].idxmin()]
best_rating = filtered_df.loc[filtered_df["Rating"].idxmax()]

st.subheader("🏆 Best Picks")

c1, c2 = st.columns(2)

with c1:
    st.markdown(f"<div class='card'><h3>Best Price</h3><p>{best_price['Title']}</p></div>", unsafe_allow_html=True)

with c2:
    st.markdown(f"<div class='card'><h3>Best Rating</h3><p>{best_rating['Title']}</p></div>", unsafe_allow_html=True)

st.markdown("---")

# -----------------------
# Products
# -----------------------
st.subheader("Products")

for i, row in filtered_df.head(10).iterrows():

    st.markdown(f"""
    <div class='card'>
        <h4>{row['Title']}</h4>
        <p>💰 {row['Price']}</p>
        <p>⭐ {row['Rating']}</p>
    </div>
    """, unsafe_allow_html=True)

    if row["Link"]:
        st.link_button("🛒 Open Product", row["Link"])

st.markdown("---")
st.caption("Developed by Roro 🚀")
