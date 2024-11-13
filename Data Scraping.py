import csv
import requests
from bs4 import BeautifulSoup
import time
import re
# Function to fetch HTML content
def fetch_html(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'}
    response = requests.get(url, headers=headers)
    return response.content if response.ok else None
  # Function to scrape car listings
def scrape_car_listings(num_pages=101):
    base_url = "https://www.avito.ma/fr/maroc/voitures_d_occasion/voiture--%C3%A0_vendre"
    car_links = []
    for page in range(1, num_pages + 1):
        url = f"{base_url}?o={page}"
        html = fetch_html(url)
        if html:
            soup = BeautifulSoup(html, "html.parser")
            # Find all links to individual car listings
            car_links.extend([a["href"] for a in soup.find_all("a", class_="sc-1jge648-0 eTbzNs")])
        else:
            print("Failed to fetch HTML content for page:", url)
    return car_links
  # Function to scrape car details
def scrape_car_details(car_url):
    car_detail={}
    details_dict = {
        'Price': 'Price',
        'ville': 'City',
        'Secteur': 'Sector',
        'Kilométrage': 'Mileage',
        'Marque': 'Brand',
        'Nombre de portes': 'Number of doors',
        'Première main': 'First hand',
        'Année-Modèle': 'Year-Model',
        'Origine': 'Origin',
        'État': 'Condition',
        'Modèle': 'Model',
        'Carburant': 'Fuel',
        'Transmission': 'Transmission',
        'Puissance Fiscale (CV)': 'Fiscal Horsepower (CV)'
    }
    html = fetch_html(car_url)
    if html:
        soup = BeautifulSoup(html, "html.parser")
        # Scrape title
        #title = soup.find('h1', class_='sc-1g3sn3w-12 jUtCZM').text.strip()
        #details_dict['Title'] = title


       # Scrape price
        price_element = soup.find('p', class_='sc-1x0vz2r-0 lnEFFR sc-1g3sn3w-13 czygWQ')
        price_text = price_element.text.strip() if price_element else ""
        if price_text:
           numeric_price = float(price_text.replace(" DH", "").replace("\u202f", "").replace(" ", ""))
        else:
            numeric_price = None  # or any other value you want to represent an empty price
        car_detail['Price'] = numeric_price


        # Scrape city
        city_element = soup.find('span', class_='sc-1x0vz2r-0 iotEHk')
        city = city_element.text.strip() if price_element else ""
        car_detail['City'] = city

        # Scrape additional details
        details_div = soup.find('div', class_='sc-qmn92k-0 cjptpz')

        if details_div:
            details = details_div.find_all('li', class_='sc-qmn92k-1 jJjeGO')
            for detail in details:
                key = detail.find('span', class_='sc-1x0vz2r-0 jZyObG').text.strip()
                value = detail.find('span', class_='sc-1x0vz2r-0 gSLYtF').text.strip()
                if key in details_dict.keys()  :
                        car_detail[details_dict[key]] = value



        details_div2 = soup.find('div', class_='sc-6p5md9-0 dsWaSi')
        if details_div2:
            # Predefined dictionary of categories and their possible values
            predefined_values = {
                "Transmission": ["Automatique", "Manuelle"],
                "Carburant": ["Essence", "Diesel", "Hybride", "Électrique"],
                "Puissance Fiscale (CV)": []  # Empty list for now, will be populated below
            }
            details = details_div2.find_all('span', class_='sc-1x0vz2r-0')
            for detail in details:
                value = detail.text.strip()
                found_category = False
                for category, possible_values in predefined_values.items():
                    if value in possible_values:
                        car_detail[details_dict[category]] = value
                        found_category = True
                        break
                if not found_category:
                    match = re.match(r'(\d+) CV', value)
                    if match:
                       car_detail[details_dict["Puissance Fiscale (CV)"]] = match.group(1)


    else:
        print("Failed to fetch HTML content for car:", car_url)

    return car_detail
  # Main function
def main():
    car_listings = scrape_car_listings()
    if car_listings:
        with open('avitoCars_Data.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Price', 'City', 'Sector', 'Mileage', 'Brand', 'Number of doors', 'First hand', 'Year-Model', 'Origin', 'Condition', 'Model', 'Fuel', 'Transmission', 'Fiscal Horsepower (CV)']
            csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            csv_writer.writeheader()
            for car_url in car_listings:
                car_details = scrape_car_details(car_url)
                if car_details:
                    csv_writer.writerow(car_details)
                    time.sleep(1)  # Add a delay to avoid overloading the server
if __name__ == "__main__":
    main()
