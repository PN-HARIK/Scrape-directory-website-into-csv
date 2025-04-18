from bs4 import BeautifulSoup
import requests
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from selenium.webdriver.chrome.options import Options
import streamlit as st

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

# for getting records

def get_articles(url):
    driver = webdriver.Chrome(options=chrome_options)
    not_last = True
    driver.get(url)
    time.sleep(1)
    article_details = {}; Name = []; Timing = []; Description = []; Address = []; Contact = []; Email = []; Website = []
    while not_last:
        articles = driver.find_elements(By.TAG_NAME, "article")
        for article in articles:
            heading = article.find_element(By.CSS_SELECTOR, ".result_hit_header h3").text
            Name.append(heading)
            try:
                timings = article.find_element(By.CSS_SELECTOR, "div.clearfix").text
            except Exception as e:
                timings = "Not Mentioned"
            Timing.append(timings)
            article_description = article.find_element(By.CSS_SELECTOR, ".result-hit-body > div")
            if article_description:
                article_description = article_description.text
            else:
                article_description = "No Description"
            Description.append(article_description)
            try:
                address = article.find_elements(By.CSS_SELECTOR, "div.mb-3 span.comma_split_line")
                print(address)
                address = [i.text for i in address]
                article_address = ",".join(address)
                if article_address == '':
                    article_address = "Not Mentioned"
            except Exception as e:
                article_address = "Not Mentioned"
            Address.append(article_address)
            contacts = article.find_elements(By.CSS_SELECTOR, "ul li a:first-of-type")
            contact = email = website = True
            numbers = []
            for i in contacts[:3]:
                if i.text == "Email":
                    Email.append(i.get_attribute("href"))
                    email = False
                elif i.text == "Website":
                    Website.append(i.get_attribute("href"))
                    website = False
                else:
                    numbers.append(i.get_attribute("href"))
                    contact = False
            if numbers:
                Contact.append(", ".join(numbers))
            if email:
                Email.append("No Email")
            if website:
                Website.append("No website link")
            if contact:
                Contact.append("No Contact")
        try:
            next_page = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.page-link[aria-label='Go to Next Page']"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", next_page)
            driver.execute_script("arguments[0].click();", next_page)
            time.sleep(1)
        except Exception as e:
            print("No more pages")
            not_last = False
    driver.quit()
    article_details.update({"Name": Name, "Timing": Timing, "Description": Description, "Address": Address, "Contact": Contact, "Email": Email, "Website": Website})
    if article_details["Name"]:
        df = pd.DataFrame(article_details)
        return df
    else:
        return
    
site_url = 'https://directory.wigan.gov.uk/kb5/wigan/fsd/home.page'

base_url = 'https://directory.wigan.gov.uk/kb5/wigan/fsd/'

# Function to fetch categories
def get_categories(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        category_urls = [i.get("href") for i in soup.select(".category-block > a")]
        category_names = [i.get_text().strip() for i in soup.select(".category-block > a > div.card-body")]
        categories = {}
        for i in range(len(category_names)):
            category_url = category_urls[i]
            if not category_url.startswith('http'):
                category_url = f'{base_url}{category_url}'
            categories[category_names[i]] = category_url
        return categories
    else:
        return None

def create_select_boxes(url):
    categories = get_categories(url)
    options = [''] + list(categories.keys())
    if not categories:
        return url
    selected_category = st.selectbox(
        f"Select a Category",
        options)
    if selected_category != "":
        selected_url = categories[selected_category]
        return create_select_boxes(selected_url)

def ui():
    st.header("Web Scraper")
    final_url = create_select_boxes(site_url)
    if st.button("Scrape Records"):
        if final_url:
            dataframe = get_articles(final_url)
            if not dataframe.empty:
                st.dataframe(dataframe)
                csv = dataframe.to_csv(index=False)
                excel_buffer = BytesIO()
                dataframe.to_excel(excel_buffer, index=False)
                excel_buffer.seek(0)
                excel_data = excel_buffer.getvalue()
                json_data = dataframe.to_json(orient="records")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.download_button("Download CSV", csv, "data.csv", "text/csv")
                with col2:
                    st.download_button("Download Excel", excel_data, "data.xlsx", "application/vnd.ms-excel")
                with col3:
                    st.download_button("Download JSON", json_data, "data.json", "application/json")
            else:
                st.write("No records found")
        else:
            st.error("Please select a valid category before scraping.")

ui()
