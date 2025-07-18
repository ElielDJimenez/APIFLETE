from flask import Flask, jsonify, request
import requests
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

def construir_url(origen, destino, contenedor="container40", weight=200, width=50, length=50, height=50, quantity=1):
    origen = origen.replace(" ", "%20")
    destino = destino.replace(" ", "%20")
    url = (
        f"https://ship.freightos.com/api/shippingCalculator?"
        f"loadtype={contenedor}&weight={weight}&width={width}&length={length}"
        f"&height={height}&origin={origen}&destination={destino}&quantity={quantity}"
    )
    return url

def consultar_flete(origen, destino, contenedor):
    url = construir_url(origen, destino, contenedor)
    logging.info(f"Consultando Freightos: {url}")
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    json = response.json()

    data = {
        "origen": origen,
        "destino": destino,
        "contenedor": contenedor,
        "fletes": []
    }

    # estructura vieja
    if "mode" in json.get("response", {}).get("estimatedFreightRates", {}):
        modo = json["response"]["estimatedFreightRates"]["mode"]
        data["fletes"].append({
            "min": modo["price"]["min"]["moneyAmount"]["amount"],
            "max": modo["price"]["max"]["moneyAmount"]["amount"],
            "transit_min": modo["transitTimes"]["min"],
            "transit_max": modo["transitTimes"]["max"]
        })
    # estructura nueva (lista)
    elif isinstance(json.get("response", {}).get("estimatedFreightRates"), list):
        for modo in json["response"]["estimatedFreightRates"]:
            data["fletes"].append({
                "min": modo["price"]["min"]["moneyAmount"]["amount"],
                "max": modo["price"]["max"]["moneyAmount"]["amount"],
                "transit_min": modo["transitTimes"]["min"],
                "transit_max": modo["transitTimes"]["max"]
            })

    return data

@app.route("/")
def home():
    return jsonify({"mensaje": "Servicio Freightos activo"}), 200

@app.route("/flete", methods=["GET"])
def obtener_flete():
    try:
        origen = request.args.get("origen", "CNCAN")
        destino = request.args.get("destino", "DOCAU")
        contenedor = request.args.get("contenedor", "container40")
        data = consultar_flete(origen, destino, contenedor)
        return jsonify(data)
    except Exception as e:
        logging.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=10000)
