from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# Function to search TESS for a trademark serial number
def search_trademark_by_name(keyword):
    search_url = f"https://tmsearch.uspto.gov/bin/showfield?f=doc&state=4803:e1sj3t.2.1&word={keyword.replace(' ', '+')}"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(search_url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract serial number
        serial_number = None
        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all("td")
                if len(cells) > 1 and cells[0].text.strip().isdigit():  # Serial numbers are numeric
                    serial_number = cells[0].text.strip()
                    break
            if serial_number:
                break

        return serial_number if serial_number else "No Serial Number Found"

    return "TESS Search Failed"

# Function to fetch trademark status from USPTO TSDR API
def check_trademark_status(serial_number):
    base_url = f"https://tsdr.uspto.gov/ts/cd/status?sn={serial_number}"
    response = requests.get(base_url)

    if response.status_code == 200:
        return {"USPTO_Status": f"Trademark status found for Serial No. {serial_number}", "link": base_url}
    
    return {"error": "USPTO TSDR API did not return data"}

# API Endpoint to Check Trademark
@app.get("/check_trademark/")
def check_trademark(name: str):
    serial_number = search_trademark_by_name(name)

    if "No Serial Number Found" in serial_number or "TESS Search Failed" in serial_number:
        return {"error": serial_number}

    uspto_result = check_trademark_status(serial_number)

    return {
        "Trademark": name,
        "Serial Number": serial_number,
        "USPTO_Result": uspto_result
    }
