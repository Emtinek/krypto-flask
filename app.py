from flask import Flask, jsonify
from flask_cors import CORS
import os  # Potrzebne do pobierania portu z ustawień systemowych
import requests  # Importujemy requests do komunikacji z API CoinGecko
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# Funkcja do pobierania kryptowalut z CoinGecko, które miały wzrost powyżej threshold w ostatnich dniach
def get_cryptos_with_pump(threshold=50, period_days=7, calm_period_days=30):
    # Pobierz listę wszystkich kryptowalut z CoinGecko
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 250,
        "page": 1,
        "sparkline": True
    }
    headers = {
        "User-Agent": "KryptoPumpFinder/1.0"
    }
    response = requests.get(url, params=params, headers=headers)

    # Sprawdź, czy odpowiedź jest poprawna
    if response.status_code != 200:
        print(f"B\u0142\u0105d podczas pobierania danych z API: {response.status_code}")
        return []

    data = response.json()

    # Logowanie liczby kryptowalut pobranych z API
    print(f"Received {len(data)} cryptocurrencies data from CoinGecko.")
    pumped_cryptos = []

    for crypto in data:
        # Pobierz historię cen ze sparkliny (ostatnie 7 dni)
        sparkline = crypto.get("sparkline_in_7d", {})
        prices = sparkline.get("price", [])

        # Ignoruj kryptowaluty, które nie mają wystarczających danych
        if not prices or len(prices) < period_days:
            print(f"Zbyt ma\u0142o danych w sparklinie dla {crypto.get('name', 'nieznana')} (ma tylko {len(prices)} dni). Pe\u0142ne dane: {crypto}")
            continue

        # Oblicz wzrost ceny w ostatnich dniach
        start_price = prices[0]
        end_price = prices[-1]
        growth = ((end_price - start_price) / start_price) * 100
        print(f"{crypto.get('name')} ({crypto.get('symbol')}): wzrost = {growth:.2f}%")

        # Sprawdź, czy wzrost przekracza threshold
        if growth < threshold:
            continue

        # Dodaj kryptowalutę do listy wynikowej
        pumped_cryptos.append({
            "name": crypto["name"],
            "symbol": crypto["symbol"],
            "start_price": start_price,
            "end_price": end_price,
            "growth": growth
        })

    # Logowanie liczby kryptowalut z pumpą
    print(f"Found {len(pumped_cryptos)} cryptocurrencies with pump.")
    return pumped_cryptos

# Strona główna
@app.route('/')
def home():
    return "Witaj w aplikacji Krypto-Pumper!"

# Funkcja zwracająca dane o kryptowalutach, które miały wzrost powyżej 50% w ostatnich 7 dniach
@app.route('/get-pumped-cryptos', methods=['GET'])
def get_pumped_cryptos():
    pumped_cryptos = get_cryptos_with_pump(50, period_days=7, calm_period_days=30)  # Zmniejszone wartości dla testów
    
    # Logowanie, jeśli zwrócone dane są puste
    if not pumped_cryptos:
        print("No pumped cryptocurrencies found.")
    
    return jsonify(pumped_cryptos)

# Uruchom serwer na odpowiednim porcie i hoście dla Rendera
if __name__ == '__main__':
    # Render wymaga bindowania do 0.0.0.0 i używania portu z ustawienia systemowego
    port = int(os.environ.get("PORT", 5000))  # Tu jest wymagany import os
    app.run(host='0.0.0.0', port=port, debug=True)