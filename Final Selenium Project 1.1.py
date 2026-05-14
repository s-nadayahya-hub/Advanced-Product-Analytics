from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
import matplotlib.pyplot as plt


options = webdriver.ChromeOptions()

options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--start-maximized")
options.add_argument("--incognito")
options.add_argument("--user-agent=Mozilla/5.0")

options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
 
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
        Object.defineProperty(navigator, 'webdriver', {
          get: () => undefined
        })
    """
})

driver.get("https://www.amazon.com/")
time.sleep(8)

search = driver.find_element(By.ID, "twotabsearchtextbox")
search.send_keys("lip gloss")
time.sleep(2)
search.send_keys(Keys.ENTER)

time.sleep(8)

for i in range(7):
    driver.execute_script("window.scrollBy(0, 1000);")
    time.sleep(2)

products = driver.find_elements(By.CSS_SELECTOR, "div[data-component-type='s-search-result']")

print("Number of Products: ", len(products))

name = []
price = []
rating = []
store = []
image = []
link = []
reviews = []

print("Data extraction is underway...")

for p in products:
    try:
        title = p.find_element(By.CSS_SELECTOR, "h2 span").text
        try:
            product_price = p.find_element(By.CSS_SELECTOR, ".a-price .a-offscreen").get_attribute("textContent")
        except:
            product_price = "NA"
        try:
            product_rating = p.find_element(By.CSS_SELECTOR, ".a-icon-alt").get_attribute("textContent")
        except:
            product_rating = "NA"
    
        try:
            product_reviews = p.find_element(By.CSS_SELECTOR, ".a-size-base.s-underline-text").text
        except:
            product_reviews = "0"
        try:
            product_image = p.find_element(By.CSS_SELECTOR, "img.s-image").get_attribute("src")
        except:
            product_image = "NA"
        try:
            product_link = p.find_element(By.CSS_SELECTOR, "h2 a").get_attribute("href")
        except:
            product_link = "NA"
        
        if title.strip() != "":
            name.append(title)
            price.append(product_price)
            rating.append(product_rating)
            reviews.append(product_reviews)
            image.append(product_image)
            link.append(product_link)
            store.append("Amazon")
            
    except:
        continue

df = pd.DataFrame({
    "Name": name,
    "Price": price,
    "Rating": rating,
    "Reviews": reviews,
    "Image": image,
    "Link": link,
    "Store": store
})

df.to_csv("amazon_lip_gloss.csv", index=False, encoding='utf-8-sig')

print(f"File Saved Sucssfully {len(df)}")

print(df[["Name", "Price"]].head(10))

driver.quit()

df["Price"] = df["Price"].str.replace("$", "", regex=False)
df["Price"] = df["Price"].str.replace(",", "", regex=False)
df["Price"] = pd.to_numeric(df["Price"], errors="coerce")

df = df.dropna(subset=["Price"])

top_products = df.sort_values(by="Price", ascending=False).head(10)
top_products["Name"] = top_products["Name"].str[:40]

plt.figure()

plt.barh(top_products["Name"], top_products["Price"])

plt.xlabel("Price")
plt.ylabel("Product Name")
plt.title("Top 10 Most Expensive Lip Gloss Products")

plt.gca().invert_yaxis()   

plt.show()