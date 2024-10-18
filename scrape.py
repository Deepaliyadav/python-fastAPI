from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time


def scrape_election_results(url):
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    
    driver.get(url)

    
    time.sleep(5)  # Adjust sleep time if necessary

    
    html = driver.page_source
    driver.quit()

    
    soup = BeautifulSoup(html, 'html.parser')

    
    table = soup.find('div', class_='custom-table').find('table')

    if not table:
        print("Table not found")
        return

    

    # Extract rows
    rows = []
    for row in table.find_all('tr')[1:]:  # Skip the header
        cols = [td.text.strip() for td in row.find_all('td')]
        
        print(f"Extracted columns: {cols}")
        rows.append(cols)


    print(f"Total rows extracted: {len(rows)}")

   

    df = pd.DataFrame(rows, columns=['S.N.', 'Candidate', 'Party', 'EVM Votes', 'Postal Votes', 'Total Votes', " '%' of Votes"])

    
    df.to_csv('election_results1.csv', index=False)
    print("Data saved to 'election_results1.csv'")


url = "https://results.eci.gov.in/AcResultGenOct2024/ConstituencywiseS0769.htm"


scrape_election_results(url)
