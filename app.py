from flask import Flask, send_file, render_template_string, url_for
import os
from MapaAutomatico import gerar_mapa_com_query

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Vale Milk • Geração de Mapas</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #F2F2F2;
            margin: 0;
            padding: 0;
        }
        header {
            background-color: #0066B3;
            color: white;
            padding: 20px;
            display: flex;
            align-items: center;
        }
        header img {
            height: 50px;
            margin-right: 20px;
        }
        h1 {
            font-size: 1.8em;
        }
        .container {
            padding: 30px;
        }
        .btn {
            background-color: #0066B3;
            color: white;
            border: none;
            padding: 12px 20px;
            margin: 10px;
            font-size: 16px;
            cursor: pointer;
            border-radius: 8px;
            transition: background-color 0.3s ease;
        }
        .btn:hover {
            background-color: #3399FF;
        }
    </style>
</head>
<body>
    <header>
        <img src="{{ url_for('static', filename='logo_valemilk.png') }}" alt="Vale Milk Logo">
        <h1>Geração de Mapas</h1>
    </header>
    <div class="container">
        <form action="/mapa_1" method="get">
            <button class="btn" type="submit">📍 Mapa com Motorista</button>
        </form>
        <form action="/mapa_2" method="get">
            <button class="btn" type="submit">🧭 Mapa por Cliente</button>
        </form>
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/mapa_1")
def mapa_motorista():
    gerar_mapa_com_query(tipo=1)
    return send_file("mapa_motorista.html")

@app.route("/mapa_2")
def mapa_cliente():
    gerar_mapa_com_query(tipo=2)
    return send_file("mapa_cliente.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
