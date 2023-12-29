from flask import Flask, render_template_string, request, jsonify
import socket
import threading
import json
from threading import Timer

app = Flask(__name__)

# Configurações do socket UDP
UDP_IP = "127.0.0.1"
UDP_PORT = 5000

# Crie um socket UDP
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Configura o socket para permitir reutilização do endereço/porta
udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Vincula o socket ao endereço IP e porta
udp_socket.bind((UDP_IP, UDP_PORT))

# Dados de pontuação (exemplo)
scores = {}


def listen_for_udp_messages():
    while True:
        data, addr = udp_socket.recvfrom(1024)  # buffer size is 1024 bytes
        data = json.loads(data.decode('utf-8'))
        print(f"Dados recebidos: {data} de {addr}")

        # Atualiza os dados de pontuação
        player = data['player']
        scores[player] = data
        print(f"Pontuação atualizada: {scores}")


# Inicie uma nova thread para ouvir mensagens UDP
threading.Thread(target=listen_for_udp_messages).start()


@app.route('/update_score', methods=['POST'])
def update_score():
    data = request.get_json()
    player = data['player']
    scores[player] = data
    print(f"Pontuação atualizada: {scores}")
    return jsonify({"message": "Pontuação atualizada com sucesso"}), 200


@app.route('/')
def index():
    # Renderiza a página HTML com as pontuações
    return render_template_string("""
   <!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <title>Pontuações dos Jogadores - EP REDES</title>
    <style>
        body {
            font-family: 'Press Start 2P', cursive;
            background-color: #000;
            color: #fff;
            text-align: center;
        }
        h1 {
            color: #0f0;
        }
        table {
            margin: auto;
            border-collapse: collapse;
        }
        th, td {
            border: 1px solid #0f0;
            padding: 10px;
            text-align: center;
        }
        th {
            background-color: #333;
        }
        tr:nth-child(even) {
            background-color: #222;
        }
        tr:nth-child(odd) {
            background-color: #111;
        }
    </style>
</head>
<body>
    <h1>Pontuações dos Jogadores</h1>
    <table>
        <tr>
            <th>Jogador</th>
            <th>Pontuação</th>
            <th>Inimigos Mortos</th>
            <th>Tiros Disparados</th>
            <th>Nível Atual</th>
            <th>Bosses Mortos</th>
            <th>Vidas do Jogador</th>
        </tr>
        {% for player, score_data in scores.items() %}
        <tr>
            <td>{{ player }}</td>
            <td>{{ score_data['score'] }}</td>
            <td>{{ score_data['enemies_killed'] }}</td>
            <td>{{ score_data['shots_fired'] }}</td>
            <td>{{ score_data['current_level'] }}</td>
            <td>{{ score_data['bosses_killed'] }}</td>
            <td>{{ score_data['player_lives'] }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>

    """, scores=scores)


if __name__ == '__main__':
    app.run(debug=True)
