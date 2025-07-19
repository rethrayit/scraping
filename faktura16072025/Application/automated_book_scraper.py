import requests
from bs4 import BeautifulSoup
import csv
import os
import glob
from datetime import datetime

# Constants
BASE_URL = "https://ksiegarniainternetowa.co.uk"
BASE_SEARCH_URL = "https://ksiegarniainternetowa.co.uk/pl/search?q="

class BookScraper:
    def __init__(self):
        self.all_results = []
        self.processed_isbns = set()
        
    def extract_isbns_from_csv_files(self, file_pattern="EU.csv"):
        """Extract ISBNs from multiple CSV files"""
        isbns = []
        csv_files = glob.glob(file_pattern)
        
        if not csv_files:
            print("No CSV files found matching the pattern")
            return isbns
            
        print(f"Found {len(csv_files)} CSV files to process")
        
        for file_path in csv_files:
            print(f"Processing file: {file_path}")
            try:
                with open(file_path, mode='r', newline='', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    file_isbns = []
                    
                    for row in reader:
                        if 'isbn' in row and row['isbn']:
                            isbn = row['isbn'].strip()
                            if isbn and isbn not in self.processed_isbns:
                                file_isbns.append(isbn)
                                self.processed_isbns.add(isbn)
                    
                    print(f"  - Extracted {len(file_isbns)} unique ISBNs")
                    isbns.extend(file_isbns)
                    
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                continue
        
        print(f"Total unique ISBNs extracted: {len(isbns)}")
        return isbns
    
    def scrape_product_link(self, isbn):
        """Scrape product link for a given ISBN"""
        search_url = f"{BASE_SEARCH_URL}{isbn}"
        
        try:
            response = requests.get(search_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            product = soup.find("div", class_="product-item")
            
            if product:
                picture_div = product.find("div", class_="picture")
                if picture_div:
                    link_tag = picture_div.find("a", href=True)
                    if link_tag:
                        return link_tag["href"]
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching search results for ISBN {isbn}: {e}")
        
        return None
    
    def scrape_book_details(self, link, isbn):
        """Scrape detailed book information from product page"""
        url = f"{BASE_URL}{link}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        book_data = {
            "Source_ISBN": isbn,
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
        
        # Extract bibliographic data from table
        table = soup.find("table", class_="bioInfo")
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
    
    def process_all_books(self, file_pattern="*.csv"):
        """Main method to process all books from multiple CSV files"""
        print("=" * 60)
        print("AUTOMATED BOOK SCRAPER STARTING")
        print("=" * 60)
        
        # Step 1: Extract ISBNs from all CSV files
        print("\n[STEP 1] Extracting ISBNs from CSV files...")
        isbns = self.extract_isbns_from_csv_files(file_pattern)
        
        if not isbns:
            print("No ISBNs found. Exiting.")
            return
        
        # Step 2: Process each ISBN
        print(f"\n[STEP 2] Processing {len(isbns)} ISBNs...")
        successful_scrapes = 0
        failed_scrapes = 0
        
        for index, isbn in enumerate(isbns, start=1):
            progress = (index / len(isbns)) * 100
            print(f"\nProcessing {index}/{len(isbns)} ({progress:.1f}%) - ISBN: {isbn}")
            
            # Get product link
            link = self.scrape_product_link(isbn)
            
            if not link:
                print(f"  ❌ No product found for ISBN: {isbn}")
                failed_scrapes += 1
                continue
            
            print(f"  ✅ Found link: {link}")
            
            # Scrape detailed book information
            book_data = self.scrape_book_details(link, isbn)
            
            if book_data:
                self.all_results.append(book_data)
                successful_scrapes += 1
                print(f"  ✅ Successfully scraped book details")
            else:
                print(f"  ❌ Failed to scrape book details")
                failed_scrapes += 1
        
        # Step 3: Save consolidated results
        print(f"\n[STEP 3] Saving consolidated results...")
        self.save_consolidated_results()
        
        # Summary
        print("\n" + "=" * 60)
        print("SCRAPING COMPLETE - SUMMARY")
        print("=" * 60)
        print(f"Total ISBNs processed: {len(isbns)}")
        print(f"Successful scrapes: {successful_scrapes}")
        print(f"Failed scrapes: {failed_scrapes}")
        print(f"Success rate: {(successful_scrapes/len(isbns)*100):.1f}%")
        
    def save_consolidated_results(self):
        """Save all results to a single consolidated CSV file"""
        if not self.all_results:
            print("No results to save.")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"consolidated_book_data_{timestamp}.csv"
        
        with open(output_filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=self.all_results[0].keys())
            writer.writeheader()
            writer.writerows(self.all_results)
        
        print(f"✅ Consolidated results saved to: {output_filename}")
        print(f"📊 Total records saved: {len(self.all_results)}")

def main():
    """Main function to run the automated book scraper"""
    scraper = BookScraper()
    
    # You can specify a pattern for your CSV files
    # Examples:
    # scraper.process_all_books("*.csv")  # Process all CSV files
    # scraper.process_all_books("EU*.csv")  # Process only files starting with EU
    # scraper.process_all_books("EU04377*.csv")  # Process specific file pattern
    
    scraper.process_all_books("*.csv")

if __name__ == "__main__":
    main()