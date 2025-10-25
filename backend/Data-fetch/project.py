# # from selenium import webdriver
# # from selenium.webdriver.common.by import By
# # import time
# # import sys

# # sys.stdout.reconfigure(encoding='utf-8')

# # driver = webdriver.Chrome()
# # query = "mobile"

# # file = 0 

# # try:
# #     for i in range(1, 5):
# #         driver.get(f"https://www.amazon.in/s?k={query}&page={i}")
# #         time.sleep(3)  

# #         elems = driver.find_elements(By.CLASS_NAME, "puisg-row")

# #         print(f"\nPage {i}: {len(elems)} items found")

# #         for elem in elems:
# #             d = elem.get_attribute("outerHTML")
# #             with open(f"backend\Data-fetch\Data/{query}_{file}.html","w" ,encoding="utf-8" )as f:
# #                 f.write(d)
# #                 file +=1
# #             # print(elem.text)

# # except Exception as e:
# #     print("Error occurred:", e)
# # finally:
# #     driver.quit()
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# import time
# import sys

# sys.stdout.reconfigure(encoding='utf-8')

# driver = webdriver.Chrome()
# query = input("Enter your search query: ")

# file = 0 

# try:
#     for i in range(1, 5):
#         driver.get(f"https://www.amazon.in/s?k={query}&page={i}")
#         time.sleep(3)  

#         elems = driver.find_elements(By.CLASS_NAME, "puisg-row")

#         print(f"\nPage {i}: {len(elems)} items found")

#         for elem in elems:
#             d = elem.get_attribute("outerHTML")
#             with open(f"backend\\Data-fetch\\Data\\{query}_{file}.html", "w", encoding="utf-8") as f:
#                 f.write(d)
#                 file += 1

# except Exception as e:
#     print("Error occurred:", e)
# finally:
#     driver.quit()





# from selenium import webdriver
# from selenium.webdriver.common.by import By
# import undetected_chromedriver as uc
# import time
# import sys

# sys.stdout.reconfigure(encoding='utf-8')
# driver = uc.Chrome()
# # driver = webdriver.Chrome()
# query = input("Enter your search query: ")

# file = 0

# # Site URLs and their corresponding main product element class names
# sites = {
#     # "amazon": {
#     #     "url": "https://www.amazon.in/s?k={query}&page={page}",
#     #     "class": "puisg-row"
#     # },
#     "flipkart": {
#         "url": "https://www.flipkart.com/search?q={query}&page={page}",
#         "class": "tUxRFH"
#     },
#     # "myntra": {
#     #     "url": "https://www.myntra.com/{query}?p={page}",
#     #     "class": "product-base"
#     # },

#     # "jiomart": {
#     #     "url": "https://www.jiomart.com/search/{query}?page={page}",
#     #     "class": "ais-InfiniteHits-item jm-col-4 jm-mt-base"  # may vary
#     # },

#     # "meesho": {
#     #     "url": "https://www.meesho.com/search?q={query}&page={page}",
#     #     "class": "sc-dkrFOg ProductListItem__GridCol-sc-1baba2g-0 ijBUXP kdQjpv"  
#     # },

#     # "alibaba": {
#     #     "url": "https://www.alibaba.com/trade/search?fsb=y&IndexArea=product_en&CatId=&SearchText={query}&page={page}",
#     #     "class": "list-no-v2-left"  # may vary
#     # },
    
# }

# try:
#     for site, config in sites.items():
#         for i in range(1, 5):
#             full_url = config["url"].format(query=query, page=i)
#             driver.get(full_url)
#             time.sleep(1)

#             elems = driver.find_elements(By.CLASS_NAME, config["class"])

#             print(f"\nSite: {site} | Page {i}: {len(elems)} items found")

#             for elem in elems:
#                 d = elem.get_attribute("outerHTML")
#                 with open(f"backend\Data-fetch\Data{site}_{query}_{file}.html", "w", encoding="utf-8") as f:
#                     f.write(d)
#                     file += 1

# except Exception as e:
#     print("Error occurred:", e)
# finally:
#     driver.quit()










from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

driver = webdriver.Chrome()
query = input("Enter your search query: ")

file = 0

# Site URLs and their corresponding main product element class names
sites = {
    "amazon": {
        "url": "https://www.amazon.in/s?k={query}&page={page}",
        "class": "puisg-row"
    },
    # "flipkart": {
    #     "url": "https://www.flipkart.com/search?q={query}&page={page}",
    #     "class": ["tUxRFH", "_2kHMtA", "_4ddWXP"]  # This will be ignored in favor of dynamic detection
    # },
    # "myntra": {
    #     "url": "https://www.myntra.com/{query}?p={page}",
    #     "class": "product-base"
    # },
    # "jiomart": {
    #     "url": "https://www.jiomart.com/search/{query}?page={page}",
    #     "class": "ais-InfiniteHits-item jm-col-4 jm-mt-base"
    # },
    # "meesho": {
    #     "url": "https://www.meesho.com/search?q={query}&page={page}",
    #     "class": "sc-dkrFOg ProductListItem__GridCol-sc-1baba2g-0 ijBUXP kdQjpv"
    # },
    # "alibaba": {
    #     "url": "https://www.alibaba.com/trade/search?fsb=y&IndexArea=product_en&CatId=&SearchText={query}&page={page}",
    #     "class": "list-no-v2-left"
    # },
}

try:
    for site, config in sites.items():
        for i in range(1, 2):
            full_url = config["url"].format(query=query, page=i)
            driver.get(full_url)
            time.sleep(2)

            if site == "flipkart":
                try:
                    close_btn = driver.find_element(By.XPATH, "//button[contains(text(),'✕')]")
                    close_btn.click()
                    time.sleep(1)
                except:
                    pass

                # Auto-detect the main product container class
                print("🔍 Auto-detecting product container class on Flipkart...")
                divs = driver.find_elements(By.XPATH, "//div")
                potential_product_divs = []

                for div in divs:
                    try:
                        children = div.find_elements(By.XPATH, "./*")
                        if len(children) >= 3:
                            html = div.get_attribute("outerHTML").lower()
                            if any(key in html for key in ["₹", "price", "rating", "review", "offer"]):
                                class_name = div.get_attribute("class")
                                if class_name:
                                    potential_product_divs.append(class_name.strip())
                    except:
                        continue

                most_common_class = None
                if potential_product_divs:
                    class_counts = Counter(potential_product_divs)
                    most_common_class = class_counts.most_common(1)[0][0]
                    print(f"✅ Detected Flipkart product class: '{most_common_class}'")

                elems = []
                if most_common_class:
                    elems = driver.find_elements(By.CLASS_NAME, most_common_class)
                else:
                    print("⚠️ Could not detect product class. Falling back to default classes.")
                    for class_name in config["class"]:
                        found = driver.find_elements(By.CLASS_NAME, class_name)
                        elems += found

            else:
                elems = driver.find_elements(By.CLASS_NAME, config["class"])

            print(f"\nSite: {site} | Page {i}: {len(elems)} items found")

            for elem in elems:
                d = elem.get_attribute("outerHTML")
                # with open(f"backend\Data-fetch\Data\{site}_{query}_{file}.html", "w", encoding="utf-8") as f:
                with open(f"backend/Data-fetch/Data/{site}_{query}_{file}.html", "w", encoding="utf-8") as f:
                    f.write(d)
                    file += 1

except Exception as e:
    print("Error occurred:", e)

finally:
    driver.quit()












