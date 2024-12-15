import os
from flask import Flask, jsonify

app = Flask(__name__)

# Strona główna
@app.route('/')
def home():
    return "Witaj w aplikacji Krypto-Pumper!"

# Funkcja zwracająca dane o kryptowalutach
@app.route('/get-pumped-cryptos', methods=['GET'])
def get_pumped_cryptos():
    # Tu na razie wstawimy testowe dane
    pumped_cryptos = [
        {"name": "Bitcoin", "symbol": "BTC", "growth": 350},
        {"name": "Ethereum", "symbol": "ETH", "growth": 400},
    ]
    return jsonify(pumped_cryptos)

# Uruchom serwer na odpowiednim porcie i hoście dla Rendera
if __name__ == '__main__':
    # Render wymaga bindowania do 0.0.0.0 i używania portu z ustawienia systemowego
    # Jeśli port nie jest ustawiony, używamy domyślnego portu 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)