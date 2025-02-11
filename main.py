from fastapi import FastAPI
import requests

app = FastAPI()

# 🔑 Set your USPTO API key here
USPTO_API_KEY = "kilpnH13NouEpLZKq2AKp3McIXnaFaNq"  # 🔴 Replace this with your real API key

# Function to fetch trademark status using USPTO TSDR API
def get_trademark_status(serial_number):
    url = f"https://tsdrapi.uspto.gov/ts/cd/casestatus/sn{serial_number}"
    headers = {
        "USPTO-API-KEY": USPTO_API_KEY,
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            return response.json()  # ✅ Returns trademark details
        else:
            return {"error": f"TSDR API Error: {response.status_code}", "message": response.text}

    except requests.exceptions.RequestException as e:
        return {"error": f"Request Failed: {str(e)}"}

# API Endpoint to Check Trademark by Serial Number
@app.get("/check_trademark/")
def check_trademark(serial_number: str):
    return get_trademark_status(serial_number)

# Run Uvicorn for Local Testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
