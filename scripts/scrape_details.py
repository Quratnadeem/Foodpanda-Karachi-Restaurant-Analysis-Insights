import pandas as pd
import time
from tqdm import tqdm
from bs4 import BeautifulSoup
import json
import undetected_chromedriver as uc

# --- Safe save helper function ---
def safe_save(df, filename="karachi_foodpanda_full_partial.csv"):
    try:
        df.to_csv(filename, index=False, encoding="utf-8-sig")
        print(f"Saved: {filename}")
    except PermissionError:
        print("Could not save file — please close it in Excel or other programs.")

# --- Load CSV ---
try:
    df = pd.read_csv("karachi_foodpanda_full_partial.csv")
    print("Resuming from partial file.")
except FileNotFoundError:
    df = pd.read_csv("karachi_foodpanda_restaurants.csv")
    df["Area"] = None
    df["Detailed Cuisine"] = None
    print("Starting from original file.")

# --- Setup undetected Chrome ---
options = uc.ChromeOptions()
options.add_argument("--start-maximized")
driver = uc.Chrome(options=options)

# --- Scraping loop ---
for i in tqdm(range(len(df))):
    if pd.notna(df.loc[i, "Area"]) and pd.notna(df.loc[i, "Detailed Cuisine"]):
        continue  # Skip already done

    try:
        url = df.loc[i, "Link"]
        print(f"\nVisiting {i+1}/{len(df)}: {url}")
        driver.get(url)
        time.sleep(6)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        # --- Extract Area ---
        area = None
        try:
            script_tag = soup.find("script", type="application/ld+json")
            if script_tag:
                json_data = json.loads(script_tag.string)
                if isinstance(json_data, list):
                    for obj in json_data:
                        if "address" in obj:
                            area = obj["address"].get("streetAddress")
                            break
                elif "address" in json_data:
                    area = json_data["address"].get("streetAddress")
            df.loc[i, "Area"] = area
            print(f"Area: {area}")
        except Exception as e:
            print(f"Area error at row {i}: {e}")
            df.loc[i, "Area"] = None

        # --- Extract Cuisine ---
        cuisine = None
        try:
            cuisine_spans = soup.select('ul.main-info__characteristics li.characteristic-list-item span')
            if cuisine_spans:
                cuisine_list = [tag.text.strip() for tag in cuisine_spans]
                cuisine = ", ".join(cuisine_list)
            df.loc[i, "Detailed Cuisine"] = cuisine
            print(f"Cuisine: {cuisine}")
        except Exception as e:
            print(f"Cuisine error at row {i}: {e}")
            df.loc[i, "Detailed Cuisine"] = None

        # --- If both missing, just log and continue ---
        if not area and not cuisine:
            print(f"Both Area and Cuisine missing at row {i}. Skipping ahead.")

        # --- Save every 500 rows ---
        if i % 500 == 0 and i != 0:
            safe_save(df)

    except Exception as e:
        print(f"Major error at row {i}: {e}")
        df.loc[i, "Area"] = None
        df.loc[i, "Detailed Cuisine"] = None

# --- Final Save ---
driver.quit()
safe_save(df)
print("Script finished. All progress saved in 'karachi_foodpanda_full_partial.csv'")

