from threading import Thread
import webbrowser
import os

# Supondo que app.py é o seu servidor Flask e Game.py é o seu jogo

def run_flask():
    os.system('python app.py')  # Pedido ao SO para rodar 'app.py'

def run_game():
    os.system('python Game.py')  # Pedido ao SO para rodar 'Game.py'

if __name__ == '__main__':
    # Cria e inicia uma thread para o servidor Flask
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    # Abre o navegador na página inicial do servidor Flask
    webbrowser.open_new('http://127.0.0.1:5000/')

    # Inicia o jogo em uma nova thread para que o servidor Flask possa rodar simultaneamente
    game_thread = Thread(target=run_game)
    game_thread.start()
