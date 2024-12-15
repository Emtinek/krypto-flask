from flask import Flask, jsonify, request

app = Flask(__name__)

# Funkcja zwracająca dane o kryptowalutach
@app.route('/get-pumped-cryptos', methods=['GET'])
def get_pumped_cryptos():
    # Tu na razie wstawimy testowe dane
    pumped_cryptos = [
        {"name": "Bitcoin", "symbol": "BTC", "growth": 350},
        {"name": "Ethereum", "symbol": "ETH", "growth": 400},
    ]
    return jsonify(pumped_cryptos)

# Uruchom serwer
if __name__ == '__main__':
    app.run(debug=True)