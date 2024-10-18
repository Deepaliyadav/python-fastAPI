from typing import Optional
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import csv
import requests
import io
import shutil
import time

from fastapi.responses import StreamingResponse
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
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.get(url)
    time.sleep(5)  # Adjust sleep time if necessary
    html = driver.page_source
    print('ok', shutil.which("google-chrome"))
    soup = BeautifulSoup(html, 'html.parser')
    # soup = BeautifulSoup(page.text, 'html.parser')
    # print(soup)
    # print(soup.prettify())
    print('soup', soup)
    scrape_page(soup)
    print(rows)

    # output = io.StringIO()
    # writer = csv.writer(output)
    # writer.writerow(head)

    # for row in rows:
    #     writer.writerow(row)
        
    # # Reset the pointer of the IO object to the beginning
    # output.seek(0)
    
    # # Send the CSV file as a response
    # response = StreamingResponse(output, media_type="text/csv")
    # response.headers["Content-Disposition"] = "attachment; filename=elections.csv"
    # driver.quit()
    
    # return response
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

    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write some example rows (header and data)
    writer.writerow(['Text', 'Author', 'Tags'])
    for quote in quotes:
        writer.writerow(quote.values())
    
    # Reset the pointer of the IO object to the beginning
    output.seek(0)
    
    # Send the CSV file as a response
    response = StreamingResponse(output, media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=quotes.csv"
    
    return response

    # return {"url": url, "quotes": quotes}


