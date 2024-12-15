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
    response = requests.get(url, params=params)
    
    # Sprawdź, czy odpowiedź jest poprawna
    if response.status_code != 200:
        print(f"Błąd podczas pobierania danych z API: {response.status_code}")
        return []

    data = response.json()

    # Logowanie liczby kryptowalut pobranych z API
    print(f"Received {len(data)} cryptocurrencies data from CoinGecko.")  # Logowanie liczby pobranych danych
    pumped_cryptos = []

    for crypto in data:
        # Pobierz podstawowe dane
        name = crypto.get("name", "unknown")
        symbol = crypto.get("symbol", "unknown")
        current_price = crypto.get("current_price", "unknown")
        price_change_percentage_24h = crypto.get("price_change_percentage_24h", 0)

        # Jeśli `sparkline_in_7d` jest pusty, pomijamy analizę wzrostu
        sparkline = crypto.get("sparkline_in_7d")
        if not sparkline:
            print(f"Brak danych o sparkline dla {name}. Wyświetlamy podstawowe dane.")
            pumped_cryptos.append({
                "name": name,
                "symbol": symbol,
                "current_price": current_price,
                "price_change_percentage_24h": price_change_percentage_24h,
                "growth": "Brak danych"
            })
            continue

        # Pobierz historię cen ze sparkliny (ostatnie 7 dni)
        prices = sparkline.get("price", [])
        if not prices or len(prices) < period_days:
            print(f"Zbyt mało danych w sparklinie dla {name} (ma tylko {len(prices)} dni). Wyświetlamy podstawowe dane.")
            pumped_cryptos.append({
                "name": name,
                "symbol": symbol,
                "current_price": current_price,
                "price_change_percentage_24h": price_change_percentage_24h,
                "growth": "Brak danych"
            })
            continue

        # Oblicz wzrost ceny w ostatnich dniach
        try:
            start_price = prices[0]
            end_price = prices[-1]
            growth = ((end_price - start_price) / start_price) * 100
        except (ZeroDivisionError, IndexError) as e:
            print(f"Błąd podczas obliczania wzrostu dla {name}: {e}. Wyświetlamy podstawowe dane.")
            pumped_cryptos.append({
                "name": name,
                "symbol": symbol,
                "current_price": current_price,
                "price_change_percentage_24h": price_change_percentage_24h,
                "growth": "Brak danych"
            })
            continue

        # Sprawdź, czy wzrost przekracza threshold
        if growth < threshold:
            pumped_cryptos.append({
                "name": name,
                "symbol": symbol,
                "current_price": current_price,
                "price_change_percentage_24h": price_change_percentage_24h,
                "growth": f"{growth:.2f}% (poniżej progu)"
            })
            continue

        # Dodaj kryptowalutę do listy wynikowej
        pumped_cryptos.append({
            "name": name,
            "symbol": symbol,
            "current_price": current_price,
            "price_change_percentage_24h": price_change_percentage_24h,
            "growth": f"{growth:.2f}% (przekracza próg)"
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