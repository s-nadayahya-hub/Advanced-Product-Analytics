import streamlit as st
import pandas as pd
import plotly.express as px
# import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import math
import webbrowser
import time
import re
from serpapi.google_search import GoogleSearch
import requests
from PIL import Image

# -----------------------
# Page Config
# -----------------------
st.set_page_config(page_title="Advanced System Pro", layout="wide")

img = Image.open("cover.jpeg")
img = img.resize((3000, 900))  # (width, height)
st.image(img)
# -----------------------
# Custom CSS
# -----------------------
st.markdown("""
    <style>
                
    /* تغيير خلفية التطبيق كاملة */
    .stApp {
        background-color: #FFFFFF;
    }

    .main { background-color: #f5f7f9; }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    /* ستايل الـ Sidebar الأيسر */
    [data-testid="stSidebar"] {
        background-color: #FFF5F7;
        border-right: 1px solid #FFE4E9;
    }

     .card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
        transition: 0.3s;
    }

    .card:hover {
        transform: scale(1.03);
    }

    .card h3 {
        color: #ff4b4b;
    }

    .card p {
        font-size: 16px;
        font-weight: bold;
    }

    .product-card{
    background:white;
    padding:20px;
    border-radius:20px;
    border:1px solid #F0F0F0;
    margin-bottom:15px;
    transition:0.3s;
    }
   .product-card:hover{
    box-shadow:0px 4px 15px rgba(0,0,0,0.08);
   }

   div.stButton > button{
     background-color:#E91E63 !important;
     color:white !important;
     border:none !important;
     border-radius:15px !important;
     width:100%;
    }

    .metric-card{
    background:white;
    padding:15px;
    border-radius:15px;
    text-align:center;
    box-shadow:0px 2px 5px rgba(0,0,0,0.05);
    }
        
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Advanced Product Analytics Pro")
st.markdown("---")


# -----------------------
# ONLINE SCRAPING FUNCTION
# -----------------------
@st.cache_data
def api_search_products(product_name):

     params = {
        "engine": "google_shopping",
        "q": product_name,
        "api_key": "9711390083a563cfc235d166143c9c226b58be0bbef9d6be577eed286d5b70a7"
     }

     search = GoogleSearch(params)
     results = search.get_dict()
     products = results.get("shopping_results", [])

     titles = []
     prices = []
     ratings = []
     stores = []
     links = []
     reviews = []

     for item in products:

         titles.append(item.get("title", "No Title"))

         
         price = item.get("price", 0)

         if isinstance(price, str):
             clean_price = re.sub(r"[^\d.]", "", price)
             try:
                 prices.append(float(clean_price))
             except:
                 prices.append(0)
         else:
             prices.append(0)

         ratings.append(item.get("rating", 0))

         
         stores.append(item.get("source", "Unknown"))

         links.append(item.get("product_link", ""))

         
         reviews.append(item.get("reviews", 0))

     df = pd.DataFrame({
        "Title": titles,
        "Price": prices,
        "Rating": ratings,
        "Store": stores,
        "Link": links,
        "Reviews": reviews
     })

     feedback = []

     for item in products:

            rating = item.get("rating", 0)
            reviews = item.get("reviews", 0)

            # approximation logic
            if rating and reviews:
                  positive = min(100, (rating / 5) * 100)
            else:
                  positive = 70  # default 

            feedback.append(positive)

     df["Positive Feedback %"] = feedback

     return df.dropna()


# -----------------------
# Load Data
# -----------------------
try:
    is_api = False

    st.sidebar.title("DATA SOURCE")

    data_source = st.sidebar.radio(
        "Choose Data Source",
        ["CSV File", "Online Scraping"]
    )

    # -----------------------
    # CSV OPTION
    # -----------------------
    if data_source == "CSV File":
        df = pd.read_csv("amazon_lip_gloss.csv")
        is_api = False

    # -----------------------
    # SCRAPING OPTION
    # -----------------------
    else:
        keyword = st.sidebar.text_input("🔍 Enter Product Keyword")

        if keyword:
            with st.spinner("Scraping products..."):
                df = api_search_products(keyword)
                is_api = True
        else:
            st.warning("Please enter a product keyword")
            st.stop()
    #cleand data
    df['Price'] = df['Price'].replace('[\$,]', '', regex=True).astype(float)
    df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce').fillna(0)
    df['Reviews'] = pd.to_numeric(df['Reviews'], errors='coerce').fillna(0)
    df['Positive Feedback %'] = pd.to_numeric(df['Positive Feedback %'], errors='coerce').fillna(0)

    if not is_api:
        max_reviews = df['Reviews'].max()

        if max_reviews == 0 or pd.isna(max_reviews):
              df['Rating'] = 3
        else:
              df['Rating'] = (df['Reviews'] / max_reviews) * 5

        df['Rating'] = df['Rating'].fillna(3).clip(0, 5)

    df["Value"] = (
        df["Rating"] * 0.6 +
        (1 / df["Price"].replace(0, 1)) * 0.4
        )

    # -----------------------
    # Sidebar
    # -----------------------
    st.sidebar.image("sidebar.png", width=100)
    st.sidebar.title("SCRAPING SYSTEM")

    search = st.sidebar.text_input("🎯 Search by Product Name")

    price_range = st.sidebar.slider(
        "💰 Price Range",
        float(df['Price'].min()),
        float(df['Price'].max()),
        (float(df['Price'].min()), float(df['Price'].max()))
    )

    stores = st.sidebar.multiselect(
        "🏪 Select Stores",
        options=df['Store'].unique(),
        default=df['Store'].unique()
    )

    with st.sidebar:          
        st.markdown("### ANALYTICS & INSIGHTS")
        st.caption("3D Graphs")
        st.caption("Charts") 
        st.caption("Heat Map")
        st.caption("Best Products")

    # -----------------------
    # Filters
    # -----------------------
    mask = (df['Price'].between(*price_range)) & (df['Store'].isin(stores))

    if search:
        mask = mask & (df['Title'].str.contains(search, case=False))

    filtered_df = df[mask]

    #   if no date 
    if filtered_df.empty:
        st.warning("No data matches your filters!")
        st.stop()

    ## 🏆 Best Picks
    best_price = filtered_df.loc[filtered_df['Price'].idxmin()]
    best_rating = filtered_df.loc[filtered_df['Rating'].idxmax()]
    best_value = filtered_df.loc[filtered_df['Value'].idxmax()]

    st.markdown("## 🏆 Best Picks")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(f"""
        <div class="card">
        <h3>💰 Best Price</h3>
        <p>{best_price['Title']}</p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="card">
        <h3>⭐ Best Rating</h3>
        <p>{best_rating['Title']}</p>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="card">
        <h3>🔥 Best Value</h3>
        <p>{best_value['Title']}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # -----------------------
    # KPIs
    # -----------------------
    m1, m2, m3, m4 = st.columns(4)

    m1.metric("Total Products", len(filtered_df))
    m2.metric("Avg Price", f"${filtered_df['Price'].mean():.2f}")
    m3.metric("Top Rating", f"⭐ {filtered_df['Rating'].max()}")
    m4.metric("Avg Feedback", f"{filtered_df['Positive Feedback %'].mean():.1f}%")

    st.markdown("---")

    # -----------------------
    # Tabs
    # -----------------------
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Market Overview",
        "🔍 Deep Analysis",
        "🏆 Smart Insights",
        "📋 Raw Data"
    ])

    # -----------------------
    # Tab 1 (Charts)
    # -----------------------
    with tab1:
        c1, c2 = st.columns([6, 4])

        with c1:
            st.subheader("Price vs Rating vs Reviews (3D)")

            # 3D CHART
            # -----------------------
            st.subheader("📈 3D Analysis")

            fig_3d = px.scatter_3d(
                    filtered_df,
                    x="Price",
                    y="Rating",
                    z="Value",
                    color="Value",
                    size="Price",
                    hover_name="Title",
                    template="plotly_dark"
                )

            st.plotly_chart(fig_3d, use_container_width=True)

        with c2:
            st.subheader("Revenue Share by Store")

            fig_pie = px.pie(
                filtered_df,
                names='Store',
                values='Price',
                hole=0.4
            )

            st.plotly_chart(fig_pie, use_container_width=True)

        # Extra Charts (Bonus)
        # -----------------------
        st.subheader("📊 Price Distribution")

        fig_bar = px.histogram(filtered_df, x="Price")
        fig_bar.update_traces(marker_color="#F88AA9")
        st.plotly_chart(fig_bar, use_container_width=True)

    # -----------------------
    # Footer
    # -----------------------
    st.markdown("✨ Created by Roro & Nadoda")    

    # -----------------------
    # Tab 2 (Heatmap)
    # -----------------------
    with tab2:

        st.subheader("🔥 Smooth KDE Heatmap")

        # selected_cols
        selected_cols = st.multiselect(
            "Select 2 Columns",
            ['Price', 'Rating', 'Reviews', 'Positive Feedback %'],
            default=['Price', 'Rating']
            )

        filtered_df = filtered_df.dropna(subset=selected_cols)

        if filtered_df[selected_cols].nunique().min() <= 1:
            st.warning("Not enough variation for heatmap")
            st.stop()

        if len(selected_cols) == 2:

            X = filtered_df[selected_cols[0]].values
            Y = filtered_df[selected_cols[1]].values

            # KDE Function
            def kde_approx(d, h):
                dn = d / h
                if dn <= 1:
                  return (1 - dn**2)**2
                return 0

            # Controls
            R = st.slider("Radius (Bandwidth)", 1.0, 10.0, 3.0)

            grid_size = st.slider("Heatmap Quality", 30, 120, 70)

            color_map = st.selectbox("Color Theme", ['hot', 'viridis'])

            if X.min() == X.max() or Y.min() == Y.max():
                    st.warning("Not enough range for heatmap")
                    st.stop()

            # Grid
            x_grid = np.linspace(X.min(), X.max(), grid_size)
            y_grid = np.linspace(Y.min(), Y.max(), grid_size)

            Z = np.zeros((grid_size, grid_size))

            # Compute KDE
            for i in range(grid_size):
                for j in range(grid_size):

                    density = 0

                    for k in range(len(X)):

                     d = math.sqrt(
                         (x_grid[i] - X[k])**2 +
                         (y_grid[j] - Y[k])**2
                     )

                     density += kde_approx(d, R)

                    Z[j][i] = density

            # Plot
            fig = px.imshow(
                Z,
              x=x_grid,
              y=y_grid,
             color_continuous_scale=color_map,
             origin='lower',
             aspect='auto'
          )

            fig.update_layout(
             height=700,
             margin=dict(l=20, r=20, t=40, b=20),
             xaxis_title=selected_cols[0],
             yaxis_title=selected_cols[1]
            )

            st.plotly_chart(fig, use_container_width=True)

        else:
                st.warning("Please select exactly 2 columns.")

    # -----------------------
    # Tab 3 (Smart Features 🔥)
    # -----------------------
    with tab3:

        st.subheader("🏆 Top Products Ranking")
        filtered_df = filtered_df.copy()
        filtered_df['Score'] = (
            filtered_df['Rating'] * 0.5 +
            filtered_df['Positive Feedback %'] * 0.3 +
            filtered_df['Reviews'] * 0.2
        )

        top_products = filtered_df.sort_values(by='Score', ascending=False).head(5)
        st.dataframe(top_products[['Title', 'Score', 'Price', 'Rating']])

        # Recommendation
        st.subheader("💡 Product Recommendation")

        query = st.text_input("Type product keyword")

        if query:
            rec = filtered_df[filtered_df['Title'].str.contains(query, case=False)]
            best = rec.sort_values(by='Rating', ascending=False).head(3)

            if not best.empty:
                st.write(best[['Title', 'Price', 'Rating']])
            else:
                st.info("No matching products found")

        # Insight
        st.subheader("📢 Smart Insight")

        best_store = filtered_df.groupby('Store')['Rating'].mean().idxmax()
        st.success(f"🏪 Best performing store: {best_store}")

        st.subheader("🏆 Top Products")

        top_ui_products = filtered_df.sort_values(
            by="Rating", 
            ascending=False
        ).head(9)

        cols = st.columns(3)

        # Use enumerate to keep the column logic (0, 1, 2) separate from the DF index
        for i, (index, row) in enumerate(top_ui_products.iterrows()):
         with cols[i % 3]:
            st.markdown(f"""
            <div class="card">
                <h4>{row['Title']}</h4>
                <p>💰 {row['Price']} EGP</p>
                <p>⭐ Rating: {row['Rating']:.1f}</p>
            </div>
            """, unsafe_allow_html=True)

            # Unique key using the dataframe index
            if st.button("🛒 Buy", key=f"buy_{index}"):

                 st.balloons()
                 st.success(f"Opening {row['Title']}...")
                 time.sleep(2)
    
                 webbrowser.open_new_tab(row['Link'])

    # -----------------------
    # Tab 4 (Data)
    # -----------------------
    with tab4:
        st.subheader("Clean Data Table")

        st.dataframe(
            filtered_df.style.background_gradient(subset=['Price'], cmap='Greens')
        )

except Exception as e:
    st.error(f"Error loading data: {e}")

st.markdown("---")
st.caption("Developed with ❤️ by Roro & Nadoda | Data Pro v3.0 🚀")
