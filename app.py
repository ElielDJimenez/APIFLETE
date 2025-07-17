from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

API_KEY = "3JAqwJpAT8V3f4ZRgB9qYYkk6B0JWkbQ"

@app.route('/flete', methods=['GET'])
def cotizar_flete():
    origen = request.args.get('origen', 'CNCAN')
    destino = request.args.get('destino', 'DOCAU')
    contenedor = request.args.get('contenedor')
    tipos = ["container20", "container40", "container40HC", "container45HC"]
    resultados = []

    contenedores_a_probar = [contenedor] if contenedor else tipos

    for tipo in contenedores_a_probar:
        params = {
            "loadtype": tipo,
            "weight": 200,
            "width": 50,
            "length": 50,
            "height": 50,
            "origin": origen,
            "destination": destino,
            "quantity": 1
        }

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        try:
            r = requests.get("https://sandbox.freightos.com/api/v1/freightEstimates", params=params, headers=headers)
            r.raise_for_status()
            data = r.json()
            rates = data.get("response", {}).get("estimatedFreightRates", [])

            if isinstance(rates, list) and len(rates) > 0:
                rate = rates[0]
            else:
                rate = data.get("response", {}).get("estimatedFreightRates", {}).get("mode", {})

            resultados.append({
                "tipo_contenedor": tipo,
                "precio_min": rate["price"]["min"]["moneyAmount"]["amount"],
                "precio_max": rate["price"]["max"]["moneyAmount"]["amount"],
                "transit_min_dias": rate["transitTimes"]["min"],
                "transit_max_dias": rate["transitTimes"]["max"]
            })

        except Exception as e:
            resultados.append({
                "tipo_contenedor": tipo,
                "error": str(e)
            })

    return jsonify({
        "origen": origen,
        "destino": destino,
        "resultados": resultados
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))