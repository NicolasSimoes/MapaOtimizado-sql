from flask import Flask, send_file, render_template_string, url_for
import os
import threading
from datetime import datetime
from MapaAutomatico import gerar_mapa_com_query

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Vale Milk • Geração de Mapas</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">

    <style>
        * {
            box-sizing: border-box;
        }
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
            margin: 0;
        }
        .container {
            padding: 60px 20px 0 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .btn {
            background-color: #0066B3;
            color: white;
            border: none;
            padding: 14px;
            font-size: 16px;
            cursor: pointer;
            border-radius: 10px;
            text-align: center;
            text-decoration: none;
            transition: background-color 0.3s ease;
            width: 280px;
            margin: 10px 0;
        }
        .btn:hover {
            background-color: #3399FF;
        }
        .btn i {
            margin-right: 8px;
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
            <button class="btn" type="submit">
                <i class="fas fa-truck"></i> 🚚 Mapa com Motorista (Rota Amanhã)
            </button>
        </form>

        <form action="/mapa_2" method="get">
            <button class="btn" type="submit">
                <i class="fas fa-calendar-day"></i> 🕐 Mapa pedidos pendentes 
            </button>
        </form>

        <form action="/mapa_3" method="get">
            <button class="btn" type="submit">
                <i class="fas fa-user"></i> 🕺 Mapa Motorista do Dia
            </button>
        </form>

        <a href="http://10.1.1.166:8000/" target="_blank" class="btn">
            <i class="fa-solid fa-map-location-dot"></i> 🌎 Mapa rotas com filtro
        </a>
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/mapa_1")
def mapa_motorista():
    return send_file("mapa_motorista.html")

@app.route("/mapa_2")
def mapa_cliente():
    return send_file("mapa_cliente.html")

@app.route("/mapa_3")
def mapa_motorista_do_dia():
    return send_file("mapa_motorista_do_dia.html")

def atualizar_mapa(tipo, nome_arquivo):
    try:
        agora = datetime.now()
        atualizar = True

        if os.path.exists(nome_arquivo):
            ultima_modificacao = datetime.fromtimestamp(os.path.getmtime(nome_arquivo))
            diff_minutos = (agora - ultima_modificacao).total_seconds() / 60
            if diff_minutos < 1:
                print(f"✅ {nome_arquivo} já atualizado há {diff_minutos:.1f} min. Pulando geração.")
                atualizar = False

        if atualizar:
            print(f"⏳ Atualizando {nome_arquivo}...")
            gerar_mapa_com_query(tipo=tipo)
            print(f"✅ {nome_arquivo} atualizado.")
    except Exception as e:
        print(f"❌ Erro ao atualizar {nome_arquivo}: {e}")

    threading.Timer(180, atualizar_mapa, args=(tipo, nome_arquivo)).start()

# Iniciar atualização automática dos três mapas
atualizar_mapa(1, "mapa_motorista.html")
atualizar_mapa(2, "mapa_cliente.html")
atualizar_mapa(3, "mapa_motorista_do_dia.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
