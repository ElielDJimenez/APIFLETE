from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

@app.route("/freight", methods=["GET"])
def obtener_flete():
    origen = request.args.get("origen", "CNCAN")
    destino = request.args.get("destino", "DOCAU")
    contenedor = request.args.get("contenedor", "container40")

    url = f"https://ship.freightos.com/api/shippingCalculator?loadtype={contenedor}&weight=200&width=50&length=50&height=50&origin={origen}&destination={destino}&quantity=1"

    try:
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()

        rates = data.get("response", {}).get("estimatedFreightRates", [])
        if isinstance(rates, list) and len(rates) > 0:
            rate = rates[0]
        else:
            rate = data.get("response", {}).get("estimatedFreightRates", {}).get("mode", {})

        resultado = {
            "origen": origen,
            "destino": destino,
            "contenedor": contenedor,
            "precio_min": rate.get("price", {}).get("min", {}).get("moneyAmount", {}).get("amount"),
            "precio_max": rate.get("price", {}).get("max", {}).get("moneyAmount", {}).get("amount"),
            "transit_min_dias": rate.get("transitTimes", {}).get("min"),
            "transit_max_dias": rate.get("transitTimes", {}).get("max")
        }
        return jsonify(resultado)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def index():
    return jsonify({"mensaje": "Microservicio Freightos (sin API key) activo"})

if __name__ == "__main__":
app.run(host="0.0.0.0", port=10000)

