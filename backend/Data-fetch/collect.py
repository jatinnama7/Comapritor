# from bs4 import BeautifulSoup
# import os

# d = {'title':[1 , 2], 'price':[3 , 4], 'link':[1 , 2]}

# for file in os.listdir("Data-fetch/Data"):
#     with open(f"Data-fetch/Data/{file}") as f:
#         html_doc = f.read() 
#     soup = BeautifulSoup(html_doc, 'html.parser')
#     t = soup.find("h2")
#     title = t.get_text()
#     print(title)

#     print(soup.prettify())
from bs4 import BeautifulSoup
import os
import json
import uuid

products = []

for file in os.listdir("Data-fetch/Data"):
    with open(f"Data-fetch/Data/{file}", encoding='utf-8') as f:
        html_doc = f.read()

    soup = BeautifulSoup(html_doc, 'html.parser')

    try:
        # ID
        product_id = str(uuid.uuid4())

        # Title
        title_tag = soup.find("h2")
        title = title_tag.get_text(strip=True) if title_tag else "No Title"

        # Price
        price_tag = soup.select_one(".a-price .a-offscreen")
        price = price_tag.get_text(strip=True) if price_tag else "No Price"

        # Description
        description_tag = soup.find("span", class_="a-truncate-full a-offscreen")
        description = description_tag.get_text(strip=True) if description_tag else "No Description"

        # Features (sample: use description split or hardcoded sample)
        features = [description] if description else []

        # Image
        image_tag = soup.find("img", class_="s-image")
        image_url = image_tag['src'] if image_tag and image_tag.has_attr('src') else "No Image"

        # Badge
        badge_tag = soup.select_one(".puis-status-badge-container")
        badge = badge_tag.get_text(strip=True) if badge_tag else None

        # Rating
        rating_tag = soup.select_one(".a-icon-alt")
        rating_text = rating_tag.get_text(strip=True).split()[0] if rating_tag else None
        rating = float(rating_text) if rating_text else None

        # Reviews Count
        reviews_tag = soup.select_one(".a-size-base.s-underline-text")
        reviews_count = int(reviews_tag.get_text(strip=True).replace(",", "")) if reviews_tag else None

        # Availability (simplified logic)
        availability = "in stock"  # Could be more dynamic with more HTML info

        # Collect the data
        # Collect the data
        product = {
            "id": product_id,
            "name": title,
            "description": description,
            "price": price,
            "features": features,
            "imageUrl": image_url,
            "badge": badge,
            "rating": rating,
            "reviewsCount": reviews_count,
            "availability": "in stock",  # Keep one of: 'in stock', 'out of stock', 'pre-order'
            "comparisonTags": ["Secure", "Fast", "Advanced"]  # Hardcoded or extract based on logic
        }


        products.append(product)

    except Exception as e:
        print("Error parsing product:", e)

# Output
print(json.dumps(products, indent=2))
