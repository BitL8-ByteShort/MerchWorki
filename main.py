from fastapi import FastAPI
import requests

app = FastAPI()

# 🔑 Your Marker API Credentials
MARKER_API_USERNAME = "cincywong"  # 🔴 Replace with your Marker API username
MARKER_API_PASSWORD = "rZn7MR4Ppb"  # 🔴 Replace with your Marker API password

# Function to check if a title contains a registered trademark
def check_trademark(title):
    base_url = f"https://markerapi.com/api/v2/trademarks/trademark/{title}/status/active/start/1/username/{MARKER_API_USERNAME}/password/{MARKER_API_PASSWORD}"
    
    try:
        response = requests.get(base_url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data and "trademarks" in data:
                return {"status": "Trademark Found", "trademark_data": data["trademarks"]}
            return {"status": "No Trademark Found"}

        return {"error": f"Marker API Error: {response.status_code}", "message": response.text}

    except requests.exceptions.RequestException as e:
        return {"error": f"Request Failed: {str(e)}"}

# API Endpoint to Check a Listing's Title for Trademarks
@app.get("/check_listing_title/")
def check_listing_title(title: str):
    return check_trademark(title)

# Run Uvicorn for Local Testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

