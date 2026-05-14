import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://www.jumia.com.eg/catalog/?q=lip+gloss"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)

soup = BeautifulSoup(response.content, "html.parser")

products = soup.find_all("article", class_="prd")

print("Number of products: ", len(products))

names = []
prices = []
links = []
images = []
ratings = []
reviews = []

for product in products:

    name = product.find("h3", class_="name")
    names.append(name.text if name else None) 
    price = product.find("div", class_="prc")
    prices.append(price.text if price else None)
     
    link = product.find("a", class_="core")
    if link:
        links.append("https://www.jumia.com.eg" + link.get("href"))
    else:
        links.append(None)
 
    img = product.find("img")
    images.append(img.get("data-src") if img else None)

    rating = product.find("div", class_="stars")
    ratings.append(rating.text if rating else None)
 
    review = product.find("span", class_="rev")
    reviews.append(review.text if review else None)

df = pd.DataFrame({
    "Name": names,
    "Price": prices,
    "Link": links,
    "Image": images,
    "Rating": ratings,
    "Reviews": reviews
})

print(df.head())
  
df.to_csv("jumia_products.csv", index=False, encoding="utf-8-sig")
