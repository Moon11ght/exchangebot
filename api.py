import requests
from config import exchange_api_key

def convert_currency(from_currency: str, to_currency: str, amount: float) -> float:
    url = f"https://api.apilayer.com/exchangerates_data/convert?to={to_currency}&from={from_currency}&amount={amount}"
    headers = {
        "apikey": exchange_api_key
    }

    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data.get("success"):
            result = round(data.get("result", 2), 2)
            return result 
        else:
            return 0.0 

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return 0.0 
    