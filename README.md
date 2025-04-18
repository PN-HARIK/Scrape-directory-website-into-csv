Scrape Directory into CSV File 🕸️📄
This project is a Streamlit-based web scraper that extracts listings from the Wigan Directory and allows you to download the data in CSV, Excel, or JSON formats.

📌 Features
Navigate through nested directory categories dynamically.

Extracts key information such as:

Name

Timing

Description

Address

Contact details

Email

Website

Supports scraping across multiple paginated results.

Headless browser scraping using Selenium.

User-friendly interface powered by Streamlit.

Download scraped data in CSV, Excel, and JSON formats.

🚀 How It Works
The Streamlit UI allows you to select a category from the Wigan directory.

On clicking "Scrape Records", it:

Launches a headless Chrome browser via Selenium.

Scrapes all articles/listings within the selected category (including paginated results).

Displays the results in a table.

Offers download buttons for CSV, Excel, and JSON files.

📁 Installation
Prerequisites
Python 3.7+

Google Chrome

ChromeDriver (compatible version)
