from flask import Flask, jsonify, request
import requests
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

def construir_url(origen, destino, contenedor):
    origen = origen.replace(" ", "%20")
    destino = destino.replace(" ", "%20")
    return (
        f"https://ship.freightos.com/api/shippingCalculator?"
        f"loadtype={contenedor}&weight=200&width=50&length=50"
        f"&height=50&origin={origen}&destination={destino}&quantity=1"
    )

def consultar_flete_contenedor(origen, destino, contenedor):
    url = construir_url(origen, destino, contenedor)
    logging.info(f"Consultando: {url}")
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    json = r.json()

    resultados = []
    if "mode" in json.get("response", {}).get("estimatedFreightRates", {}):
        modo = json["response"]["estimatedFreightRates"]["mode"]
        resultados.append({
            "contenedor": contenedor,
            "min": modo["price"]["min"]["moneyAmount"]["amount"],
            "max": modo["price"]["max"]["moneyAmount"]["amount"],
            "transit_min": modo["transitTimes"]["min"],
            "transit_max": modo["transitTimes"]["max"]
        })
    elif isinstance(json.get("response", {}).get("estimatedFreightRates"), list):
        for modo in json["response"]["estimatedFreightRates"]:
            resultados.append({
                "contenedor": contenedor,
                "min": modo["price"]["min"]["moneyAmount"]["amount"],
                "max": modo["price"]["max"]["moneyAmount"]["amount"],
                "transit_min": modo["transitTimes"]["min"],
                "transit_max": modo["transitTimes"]["max"]
            })
    return resultados

@app.route("/")
def home():
    return jsonify({"mensaje": "Servicio Freightos activo"}), 200

@app.route("/flete", methods=["GET"])
def obtener_fletes():
    try:
        origen = request.args.get("origen", "CNCAN")
        destino = request.args.get("destino", "DOCAU")
        tipos = ["container20", "container40", "container40hc", "container45hc"]

        fletes = []
        for tipo in tipos:
            try:
                fletes += consultar_flete_contenedor(origen, destino, tipo)
            except Exception as e:
                logging.warning(f"No se pudo obtener flete para {tipo}: {e}")

        return jsonify({
            "origen": origen,
            "destino": destino,
            "fletes": fletes
        })

    except Exception as e:
        logging.error(f"Error general: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=10000)
