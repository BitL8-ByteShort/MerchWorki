from fastapi import FastAPI
import requests
from fuzzywuzzy import fuzz
from bs4 import BeautifulSoup

app = FastAPI()

# Function to query USPTO Basic Search API
def search_uspto_trademarks(keyword):
    base_url = "https://assignment-api.uspto.gov/trademark/basicSearch"
    params = {"searchExpression": keyword, "fromRecord": 0, "toRecord": 5}  # Get top 5 results

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        if "results" in data:
            return data["results"]  # Extract trademark data
    return []

# Function to check similarity
def check_trademark_similarity(listing_name, trademarks):
    results = []
    
    for trademark in trademarks:
        name = trademark.get("markLiteral", "")  # Adjusted for Basic Search API
        similarity = fuzz.ratio(listing_name.lower(), name.lower())

        if similarity > 60:  # Lowered threshold to catch more matches
            results.append({
                "Trademark": name,
                "Similarity": similarity,
                "Serial Number": trademark.get("serialNumber", "N/A"),
                "Registration Number": trademark.get("registrationNumber", "N/A"),
                "Status": trademark.get("statusCode", "N/A"),
                "Live/Dead": "LIVE" if trademark.get("statusCode", "").lower() == "live" else "DEAD"
            })
    
    return results

# Function to scrape TESS for trademarks
def scrape_tess(keyword):
    url = f"https://tmsearch.uspto.gov/bin/gate.exe?f=searchss&state=4803:6oij73.1.1&p_search=searchstr&expr={keyword.replace(' ', '+')}&p_s_ALL=ALL&p_op_ALL=AND"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        results = soup.find_all("tr")

        trademark_names = []
        for row in results:
            cells = row.find_all("td")
            if len(cells) > 1:
                trademark_names.append(cells[0].text.strip())

        return trademark_names
    return []

# API Endpoint to Check Trademark
@app.get("/check_trademark/")
def check_trademark(name: str):
    # Search USPTO Basic Search API
    trademarks = search_uspto_trademarks(name)
    matches = check_trademark_similarity(name, trademarks)

    # Search TESS for additional verification
    tess_results = scrape_tess(name)

    return {
        "USPTO_Matches": matches,
        "TESS_Results": tess_results
    }

# Run Uvicorn (Fix Port Issue for Render)
if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.environ.get("PORT", 8000))  # Render assigns a PORT dynamically
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

