#-----------------------------
# This script scrapes product links from a bookstore website based on ISBNs provided in a CSV file.
# It reads ISBNs from a source CSV file, searches for each ISBN on the website, and writes the found product links to a results CSV file.
# It uses the requests library to fetch web pages and BeautifulSoup to parse HTML content.
# -----------------------------
import requests
from bs4 import BeautifulSoup
import csv

# Input and output file names
SOURCE_FILE = "source.csv"
RESULTS_FILE = "results.csv"

# Base URL for search
BASE_SEARCH_URL = "https://ksiegarniainternetowa.co.uk/en/search?q="

def scrape_product_link(isbn):
    """Scrape product link for a given ISBN."""
    search_url = f"{BASE_SEARCH_URL}{isbn}"
    response = requests.get(search_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Find first product item (if exists)
    product = soup.find("div", class_="product-item")

    if product:
        picture_div = product.find("div", class_="picture")
        link_tag = picture_div.find("a", href=True)

        if link_tag:
            return link_tag["href"]

    # Return None if no product found
    return None

def main():
    # Read source.csv and collect all ISBNs
    with open(SOURCE_FILE, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        isbns = [row['isbn'].strip() for row in reader]

    # Prepare to write results
    with open(RESULTS_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["isbn", "link"])  # Header row

        for isbn in isbns:
            print(f"Scraping for ISBN: {isbn}")
            link = scrape_product_link(isbn)

            if link:
                print(f"Found link: {link}")
            else:
                print("No product found.")

            # Write result (save None if no link found)
            writer.writerow([isbn, link])

    print(f"Results saved to {RESULTS_FILE}")

if __name__ == "__main__":
    main()