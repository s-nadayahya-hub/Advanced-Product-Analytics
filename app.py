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
