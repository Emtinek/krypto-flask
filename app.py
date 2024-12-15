from flask import Flask, jsonify
from flask_cors import CORS
import os  # Potrzebne do pobierania portu z ustawień systemowych
import requests  # Importujemy requests do komunikacji z API CoinGecko
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# Funkcja do pobierania kryptowalut z CoinGecko, które miały wzrost powyżej threshold w ostatnich 7 dniach
def get_cryptos_with_pump(threshold=200, period_days=10, calm_period_days=90):
    # Pobierz listę wszystkich kryptowalut z CoinGecko
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 250,
        "page": 1,
        "sparkline": True
    }
    response = requests.get(url, params=params)
    data = response.json()

    pumped_cryptos = []
    for crypto in data:
        # Pobierz historię cen ze sparkliny (ostatnie 7 dni)
        prices = crypto.get("sparkline_in_7d", {}).get("price", [])
        if len(prices) < period_days:
            continue
        
        # Oblicz wzrost ceny w ostatnich 10 dniach
        start_price = prices[0]
        end_price = prices[-1]
        growth = ((end_price - start_price) / start_price) * 100
        
        # Sprawdź, czy wzrost przekracza threshold (np. 200%)
        if growth < threshold:
            continue

        # Teraz sprawdzamy, czy przed tym wzrostem przez ostatnie 3 miesiące kryptowaluta była "spokojna"
        # Pobierz dane historyczne z ostatnich 3 miesięcy (około 90 dni)
        calm_period_start = (datetime.now() - timedelta(days=calm_period_days)).strftime('%d-%m-%Y')
        historical_url = f"https://api.coingecko.com/api/v3/coins/{crypto['id']}/market_chart"
        historical_params = {
            "vs_currency": "usd",
            "days": calm_period_days,
            "interval": "daily"
        }
        historical_response = requests.get(historical_url, params=historical_params)
        
        # Upewnij się, że odpowiedź zawiera dane
        if historical_response.status_code != 200:
            print(f"Błąd podczas pobierania danych historycznych dla {crypto['name']}")
            continue
        
        historical_data = historical_response.json()

        # Upewnij się, że dane historyczne są dostępne
        if 'prices' not in historical_data:
            print(f"Brak danych historycznych dla {crypto['name']}")
            continue

        # Sprawdź, czy przez ostatnie 90 dni nie było większych wzrostów (czyli wzrosty były mniejsze niż np. 20%)
        calm = True
        for i in range(len(historical_data["prices"]) - 1):
            start_historical_price = historical_data["prices"][i][1]
            end_historical_price = historical_data["prices"][i + 1][1]
            historical_growth = ((end_historical_price - start_historical_price) / start_historical_price) * 100
            if historical_growth > 20:  # Załóżmy, że wzrosty większe niż 20% to "aktywność"
                calm = False
                break

        if calm:
            pumped_cryptos.append({
                "name": crypto["name"],
                "symbol": crypto["symbol"],
                "start_price": start_price,
                "end_price": end_price,
                "growth": growth
            })

    return pumped_cryptos

# Strona główna
@app.route('/')
def home():
    return "Witaj w aplikacji Krypto-Pumper!"

# Funkcja zwracająca dane o kryptowalutach, które miały wzrost powyżej 200% w ostatnich 10 dniach i były spokojne przez 3 miesiące
@app.route('/get-pumped-cryptos', methods=['GET'])
def get_pumped_cryptos():
    pumped_cryptos = get_cryptos_with_pump(200, period_days=10, calm_period_days=90)
    return jsonify(pumped_cryptos)

# Uruchom serwer na odpowiednim porcie i hoście dla Rendera
if __name__ == '__main__':
    # Render wymaga bindowania do 0.0.0.0 i używania portu z ustawienia systemowego
    # Jeśli port nie jest ustawiony, używamy domyślnego portu 5000
    port = int(os.environ.get("PORT", 5000))  # Tu jest wymagany import os
    app.run(host='0.0.0.0', port=port, debug=True)
