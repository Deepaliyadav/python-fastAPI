# Scrape basic website and store data in csv file

import csv
import requests
from bs4 import BeautifulSoup

quotes = []
def scrape_page(soup):
    quote_elements = soup.find_all('div', class_='quote')

    for quote in quote_elements:
        text = quote.find('span', class_='text').text
        author = quote.find('small', class_='author').text
        tag_elements = quote.find('div', class_='tags').find_all('a', class_='tag')
        tags = []
        for tag_element in tag_elements:
            tags.append(tag_element.text)
        quotes.append(
            {
                'text': text,
                'author': author,
                'tags': ', '.join(tags)
            }
        )

base_url = 'http://quotes.toscrape.com'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
}

page = requests.get(base_url, headers=headers)
soup = BeautifulSoup(page.text, 'html.parser')
scrape_page(soup)

# getting the "Next →" HTML element
next_li_element = soup.find('li', class_='next')
print(next_li_element)
# if there is a next page to scrape
while next_li_element is not None:
    next_page_relative_url = next_li_element.find('a', href=True)['href']

    # getting the new page
    print(base_url + next_page_relative_url)
    page = requests.get(base_url + next_page_relative_url, headers=headers)

    # parsing the new page
    soup = BeautifulSoup(page.text, 'html.parser')

    # scraping the new page
    scrape_page(soup)

    # looking for the "Next →" HTML element in the new page
    next_li_element = soup.find('li', class_='next')

csv_file = open('quotes.csv', 'w', encoding='utf-8', newline='')

writer = csv.writer(csv_file)

writer.writerow(['Text', 'Author', 'Tags'])

for quote in quotes:
    writer.writerow(quote.values())

csv_file.close()