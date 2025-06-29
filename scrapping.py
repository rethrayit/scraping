import requests
from bs4 import BeautifulSoup
import csv
import os

# Constants
BASE_URL = "https://ksiegarniainternetowa.co.uk"
LINKS_DB_FILE = "ready_links.csv"

# Read links from CSV
def read_links():
    links = []
    with open(LINKS_DB_FILE, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            links.append(row['link'].strip())
    return links

# Scraping function
def scrape_page(link):
    url = f"{BASE_URL}{link}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", class_="bioInfo")

    book_data = {
        "Link": link,
        "Rodzaj (nośnik)": None,
        "Dział": None,
        "Autor": None,
        "Tytuł": None,
        "Tytuł originału": None,
        "Język": None,
        "Wydawca": None,
        "Rok wydania": None,
        "Rodzaj oprawy": None,
        "Wymiary": None,
        "Liczba stron": None,
        "Ciężar": None,
        "Wydano": None,
        "ISBN": None,
        "EAN/UPC": None,
        "Image": None,
        "Description": None,
        "Kategoria": None
    }

    # Extract product image
    picture_div = soup.find("div", class_="picture")
    if picture_div:
        img_tag = picture_div.find("img", {"id": lambda x: x and x.startswith("main-product-img")})
        if img_tag and "src" in img_tag.attrs:
            book_data["Image"] = img_tag["src"]

    # Extract product description
    description_div = soup.find("div", class_="full-description")
    if description_div:
        book_data["Description"] = description_div.get_text(" ", strip=True)

    # Extract product title from product-name div
    product_name_div = soup.find("div", class_="product-name")
    if product_name_div:
        h1_tag = product_name_div.find("h1", itemprop="name")
        if h1_tag:
            book_data["Tytuł"] = h1_tag.get_text(strip=True)

    # Extract categories (ignoring unwanted ones)
    excluded_categories = {"Aktualne promocje", "Szybka wysyłka", "Promocje!"}
    categories_div = soup.find("div", class_="allCategoriesBox")

    if categories_div:
        categories = [
            a.get_text(strip=True)
            for a in categories_div.find_all("a", class_="CategoriesBox_SingleCategory")
            if a.get_text(strip=True) not in excluded_categories
        ]
        book_data["Kategoria"] = ", ".join(categories) if categories else None

    # Extract bibliographic data
    if table:
        for row in table.find_all("tr"):
            label = row.find("th", class_="bioInfoLabel")
            data = row.find("th", class_="bioInfoData")

            if not label or not data:
                continue

            label_text = label.get_text(strip=True)
            data_text = data.get_text(" ", strip=True)

            if "Rodzaj (nośnik)" in label_text:
                book_data["Rodzaj (nośnik)"] = data_text
            elif "Dział" in label_text:
                book_data["Dział"] = data_text
            elif "Autor" in label_text:
                book_data["Autor"] = data_text
            elif "Tytuł originału" in label_text:
                book_data["Tytuł originału"] = data_text
            elif "Język" in label_text:
                book_data["Język"] = data_text
            elif "Wydawca" in label_text:
                book_data["Wydawca"] = data_text
            elif "Rok wydania" in label_text:
                book_data["Rok wydania"] = data_text
            elif "Rodzaj oprawy" in label_text:
                book_data["Rodzaj oprawy"] = data_text
            elif "Wymiary" in label_text:
                book_data["Wymiary"] = data_text
            elif "Liczba stron" in label_text:
                book_data["Liczba stron"] = data_text
            elif "Ciężar" in label_text:
                book_data["Ciężar"] = data_text
            elif "Wydano" in label_text:
                book_data["Wydano"] = data_text
            elif "ISBN" in label_text:
                book_data["ISBN"] = data_text
            elif "EAN/UPC" in label_text:
                book_data["EAN/UPC"] = data_text

    return book_data

# Main function to process all links and split results into batches of 200
def main():
    links = read_links()
    total_links = len(links)
    batch_size = 200
    batch_number = 1

    for i in range(0, total_links, batch_size):
        batch_links = links[i:i+batch_size]
        results = []

        for index, link in enumerate(batch_links, start=1):
            overall_index = i + index
            progress = (overall_index / total_links) * 100
            print(f"Scraping {overall_index}/{total_links} ({progress:.2f}%) - {link}")

            try:
                book_data = scrape_page(link)
                if book_data:  # Ensure valid data before adding
                    results.append(book_data)
            except Exception as e:
                print(f"Failed to scrape {link}: {e}")

        # Avoid writing empty results
        if results:
            output_filename = f"test6_results_batch_{batch_number}.csv"
            with open(output_filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)

            print(f"Saved batch {batch_number} to {output_filename}")

        batch_number += 1

if __name__ == "__main__":
    main()