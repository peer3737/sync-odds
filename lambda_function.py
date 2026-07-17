import json
from datetime import datetime
from zoneinfo import ZoneInfo
import requests
import os

UPDATE_KEY = os.getenv("UPDATE_KEY")
FASTAPI_ENDPOINT = os.getenv("FASTAPI_ENDPOINT")
API_KEY = os.getenv("API_KEY")
SPORT_KEY = os.getenv("SPORT_KEY")
ODD_BASE_URL = os.getenv("ODD_BASE_URL")

def lambda_handler(event, context):
    odds = get_odds()

    for match in odds:
        match['start_date_time'] = match['start_date_time'].isoformat()
        print(match)
    headers = {
        "X-API-KEY": API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.put(f"https://{FASTAPI_ENDPOINT}/odds/update", json=odds, headers=headers)
    print("Status Code:", response.status_code)
    print("Response Text:", response.text)
def get_odds():

    base_url = f"https://{ODD_BASE_URL}"
    resource = f"/v4/sports/{SPORT_KEY}/odds/?apiKey={API_KEY}&regions=eu"
    url = f"{base_url}{resource}"

    response = requests.get(url).json()
    wedstrijden = []

    for item in response:
        # Initialisatie van totalen
        total_1, total_2, total_x, bookmakers_aantal = 0, 0, 0, 0

        for bookmaker in item['bookmakers']:
            # Check of alle drie de outcomes aanwezig zijn in de eerste market
            outcomes = bookmaker['markets'][0]['outcomes']
            if len(outcomes) == 3:
                for outcome in outcomes:
                    if outcome['name'].lower() == item["home_team"].lower():
                        total_1 += outcome['price']
                    elif outcome['name'].lower() == item["away_team"].lower():
                        total_2 += outcome['price']
                    else:
                        total_x += outcome['price']
                bookmakers_aantal += 1

        if bookmakers_aantal > 0:
            avg_1 = round(total_1 / bookmakers_aantal, 2)
            avg_2 = round(total_2 / bookmakers_aantal, 2)
            avg_x = round(total_x / bookmakers_aantal, 2)

            body = {
                "home_team": item["home_team"],
                "away_team": item["away_team"],
                "start_date_time": datetime.fromisoformat(item["commence_time"].replace('Z', '+00:00')).astimezone(
                    ZoneInfo("Europe/Amsterdam")),
                "1": avg_1,
                "2": avg_2,
                "x": avg_x,

            }
            wedstrijden.append(body)

    return wedstrijden


lambda_handler(None, None)
