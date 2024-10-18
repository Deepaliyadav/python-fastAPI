from typing import Optional
import csv
import requests
from bs4 import BeautifulSoup

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (adjust this for production to specific domains)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get('/scrapegovt')
def read_item(url: Optional[str] = None):
    # url = 'https://results.eci.gov.in/AcResultGenOct2024/ConstituencywiseS0769.htm'
    head = []
    rows = []
    def scrape_page(soup):
        rows_ele = soup.find_all('tr')
        print('rows_ele', rows_ele)
        # print(s)
        for row in rows_ele:
            td = row.find_all('td')  # Find all <td> elements in the current row
            th = row.find_all('th')  # Find all <th> elements in the current row
            arr = []
            for index, cell in enumerate(td):
                cell_text = cell.get_text(strip=True)
                # Check if the text contains a date-like format (e.g., 8/8)
                if '/' in cell_text and len(cell_text.split('/')) == 2:
                    cell_text = f"'{cell_text}"  # Prepend apostrophe to prevent date conversion
                arr.append(cell_text)

            for cell in th:
                head.append(cell.get_text(strip=True))
            rows.append(arr)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    }
    cookies = {
    "your_cookie_name": "your_cookie_value"
    }
    page = requests.get(url, headers=headers, cookies=cookies, verify=True)
    soup = BeautifulSoup(page.text, 'html.parser')
    print(soup)
    scrape_page(soup)
    print(rows)
    return {"url": url, "columns": head, "rows": rows}


@app.get("/scrape")
def read_item(url: Optional[str] = None):
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

    return {"url": url, "quotes": quotes}


    # csv_file = open('quotes.csv', 'w', encoding='utf-8', newline='')

    # writer = csv.writer(csv_file)

    # writer.writerow(['Text', 'Author', 'Tags'])

    # for quote in quotes:
    #     writer.writerow(quote.values())

    # csv_file.close()

