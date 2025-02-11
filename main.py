from fastapi import FastAPI
import requests

app = FastAPI()

# Function to search for a trademark's serial number using USPTO Assignment API
def search_trademark_by_name(keyword):
    base_url = "https://assignment-api.uspto.gov/trademark/basicSearch"
    params = {"searchExpression": keyword, "fromRecord": 0, "toRecord": 5}  # Get up to 5 results

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        if "results" in data and len(data["results"]) > 0:
            return data["results"][0]["serialNumber"]  # Extract first trademark serial number

    return "No Serial Number Found"

# Function to fetch trademark status using USPTO TSDR API
def check_trademark_status(serial_number):
    base_url = f"https://tsdrapi.uspto.gov/ts/cd/casestatus/sn{serial_number}"
    
    response = requests.get(base_url)

    if response.status_code == 200:
        return response.json()  # Returns full trademark details
    
    return {"error": "USPTO TSDR API did not return data"}

# API Endpoint to Check Trademark by Name
@app.get("/check_trademark/")
def check_trademark(name: str):
    serial_number = search_trademark_by_name(name)

    if serial_number == "No Serial Number Found":
        return {"error": "No trademark found for this name"}

    uspto_result = check_trademark_status(serial_number)

    return {
        "Trademark": name,
        "Serial Number": serial_number,
        "USPTO_Result": uspto_result
    }

# Run Uvicorn (Fix Port Issue for Render Deployment)
if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.environ.get("PORT", 8000))  # Render assigns a PORT dynamically
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
