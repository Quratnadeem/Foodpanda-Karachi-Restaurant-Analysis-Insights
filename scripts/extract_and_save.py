from bs4 import BeautifulSoup
import pandas as pd

# Load saved HTML
with open("page.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")
vendors = soup.select('a[data-testid^="vendor-tile-new-link"]')

data = []

for vendor in vendors:
    name_tag = vendor.find("div", class_="vendor-name")
    rating_tag = vendor.select_one('[data-testid="review-and-rating"]')
    cuisine_tag = vendor.select_one('[data-testid="vendor-info-row-text"]')
    discount_tags = vendor.select('div[data-testid="revamped-primary-tag"] span.bds-c-tag__label')
    img_tag = vendor.find("img")
    link = vendor.get("href")

    # New: Review Count
    review_count_tag = vendor.select_one('span.bds-c-rating__label-secondary')

    # New: Delivery Time (approximate)
    delivery_time_tag = vendor.find("div", string=lambda text: text and "min" in text)

    # New: Area / Location (secondary text, different from cuisine)
    secondary_texts = vendor.find_all("div", class_="vendor-info-row-text")
    area = None
    if len(secondary_texts) > 1:
        area = secondary_texts[1].text.strip()  # second row usually area

    name = name_tag.text.strip() if name_tag else None
    rating = rating_tag.text.strip() if rating_tag else None
    cuisine = cuisine_tag.text.strip() if cuisine_tag else None
    discounts = ", ".join(tag.text.strip() for tag in discount_tags) if discount_tags else None
    image_url = img_tag.get("src") if img_tag else None
    full_link = "https://www.foodpanda.pk" + link if link else None
    review_count = review_count_tag.text.strip() if review_count_tag else None
    delivery_time = delivery_time_tag.text.strip() if delivery_time_tag else None

    data.append({
        "Name": name,
        "Rating": rating,
        "Review Count": review_count,
        "Cuisine": cuisine,
        "Area": area,
        "Delivery Time": delivery_time,
        "Discounts": discounts,
        "Image URL": image_url,
        "Link": full_link
    })


df = pd.DataFrame(data)
df.to_csv("karachi_foodpanda_restaurants.csv", index=False, encoding="utf-8-sig")
print("Data saved to 'karachi_foodpanda_restaurants.csv'")
print(f"Total restaurants extracted: {len(df)}")

