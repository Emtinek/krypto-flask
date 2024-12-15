from flask import Flask, jsonify
from flask_cors import CORS
import os  # Potrzebne do pobierania portu z ustawień systemowych
import requests  # Importujemy requests do komunikacji z API CoinGecko

app = Flask(__name__)
CORS(app)

# Funkcja do pobierania kryptowalut z CoinGecko, które miały wzrost powyżej threshold w ostatnich 7 dniach
def get_cryptos_with_pump(threshold=200):
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
        if len(prices) < 2:
            continue
        
        # Oblicz wzrost ceny
        start_price = prices[0]
        end_price = prices[-1]
        growth = ((end_price - start_price) / start_price) * 100
        
        # Sprawdź kryterium wzrostu
        if growth > threshold:
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

# Funkcja zwracająca dane o kryptowalutach, które miały wzrost powyżej 200% w ostatnich 7 dniach
@app.route('/get-pumped-cryptos', methods=['GET'])
def get_pumped_cryptos():
    pumped_cryptos = get_cryptos_with_pump(200)  # Ustawiamy próg na 200%
    return jsonify(pumped_cryptos)

# Uruchom serwer na odpowiednim porcie i hoście dla Rendera
if __name__ == '__main__':
    # Render wymaga bindowania do 0.0.0.0 i używania portu z ustawienia systemowego
    # Jeśli port nie jest ustawiony, używamy domyślnego portu 5000
    port = int(os.environ.get("PORT", 5000))  # Tu jest wymagany import os
    app.run(host='0.0.0.0', port=port, debug=True)
