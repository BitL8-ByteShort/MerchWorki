from fastapi import FastAPI
import requests
import os

app = FastAPI()

# Load USPTO API Key from Environment Variables
USPTO_API_KEY = os.getenv("USPTO_API_KEY")

# Function to search for a trademark's serial number
def search_trademark_by_name(keyword):
    base_url = "https://developer.uspto.gov/ds-api/trademark/v1/search"
    params = {"q": f'"{keyword}"'}  # Search for exact trademark name
    headers = {"USPTO-API-KEY": USPTO_API_KEY}

    try:
        response = requests.get(base_url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if "results" in data and len(data["results"]) > 0:
                return data["results"][0]["serialNumber"]  # Get first serial number
            return "No Serial Number Found"
        return f"USPTO Search API Error: {response.status_code}"
    
    except requests.exceptions.RequestException as e:
        return f"Request Failed: {str(e)}"

# Function to fetch trademark status using USPTO TSDR API
def check_trademark_status(serial_number):
    base_url = f"https://tsdrapi.uspto.gov/ts/cd/casestatus/sn{serial_number}"
    headers = {"USPTO-API-KEY": USPTO_API_KEY}

    try:
        response = requests.get(base_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return response.json()  # Return full trademark details
        return {"error": f"TSDR API Error: {response.status_code}"}
    
    except requests.exceptions.RequestException as e:
        return {"error": f"Request Failed: {str(e)}"}

# API Endpoint to Check Trademark by Name
@app.get("/check_trademark/")
def check_trademark(name: str):
    serial_number = search_trademark_by_name(name)

    if "No Serial Number Found" in serial_number or "Error" in serial_number:
        return {"error": serial_number}

    uspto_result = check_trademark_status(serial_number)

    return {
        "Trademark": name,
        "Serial Number": serial_number,
        "USPTO_Result": uspto_result
    }

# Run Uvicorn for Local Testing
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))  # Render assigns a PORT dynamically
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)


