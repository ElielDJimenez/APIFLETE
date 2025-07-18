from flask import Flask, request, jsonify
import requests
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route("/")
def home():
    return jsonify({"mensaje": "API de fletes activa"}), 200

@app.route("/flete", methods=["GET"])
def obtener_flete():
    try:
        origen = request.args.get("origen")
        destino = request.args.get("destino")
        contenedor = request.args.get("contenedor")  # container20, container40, boxes

        if not origen or not destino or not contenedor:
            return jsonify({"error": "Parámetros requeridos: origen, destino y contenedor"}), 400

        url = f"https://ship.freightos.com/api/shippingCalculator?loadtype={contenedor}&weight=200&width=50&length=50&height=50&origin={origen}&destination={destino}&quantity=1"
        logging.info(f"Llamando a URL: {url}")
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        data = response.json()
        flete = {}

        if "mode" in data.get("response", {}).get("estimatedFreightRates", {}):
            modo = data["response"]["estimatedFreightRates"]["mode"]
            flete = {
                "min": modo["price"]["min"]["moneyAmount"]["amount"],
                "max": modo["price"]["max"]["moneyAmount"]["amount"],
                "tiempoMin": modo["transitTimes"]["min"],
                "tiempoMax": modo["transitTimes"]["max"]
            }
        elif data.get("response", {}).get("estimatedFreightRates"):
            modo = data["response"]["estimatedFreightRates"][0]
            flete = {
                "min": modo["price"]["min"]["moneyAmount"]["amount"],
                "max": modo["price"]["max"]["moneyAmount"]["amount"],
                "tiempoMin": modo["transitTimes"]["min"],
                "tiempoMax": modo["transitTimes"]["max"]
            }
        else:
            return jsonify({"error": "No se encontraron tarifas"}), 404

        return jsonify(flete)

    except Exception as e:
        logging.error(f"Error inesperado: {e}")
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
