import os
import requests
from flask import Flask, request
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

app = Flask(__name__)

# Configurações extraídas do ambiente
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

# Dicionário de setores - Fácil de expandir
SETORES = {
    "1": ("Financeiro", "+55 11 99999-1111"),
    "2": ("Projetos", "+55 11 99999-2222"),
    "3": ("RH", "+55 11 99999-3333"),
}

# --- FUNÇÕES DE ENVIO ---

def enviar_mensagem_texto(numero, texto):
    """Envia uma mensagem de texto simples"""
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "text",
        "text": {"body": texto}
    }
    return requests.post(url, headers=headers, json=payload)

def enviar_menu_lista(numero):
    """Envia o menu interativo em formato de lista (Profissional)"""
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Montando as linhas da lista dinamicamente com base no dicionário SETORES
    rows = []
    for id_setor, (nome, _) in SETORES.items():
        rows.append({
            "id": id_setor,
            "title": nome,
            "description": f"Falar com o setor de {nome.lower()}"
        })

    payload = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {"type": "text", "text": "Atendimento Automatizado"},
            "body": {"text": "Olá! 👋 Seja bem-vindo.\nPara continuar, selecione o setor desejado na lista abaixo:"},
            "footer": {"text": "Selecione uma opção para ver o contato"},
            "action": {
                "button": "Ver Opções",
                "sections": [{
                    "title": "Setores Disponíveis",
                    "rows": rows
                }]
            }
        }
    }
    return requests.post(url, headers=headers, json=payload)

# --- ROTAS DO WEBHOOK ---

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Erro de verificação", 403

@app.route("/webhook", methods=["POST"])
def receive_message():
    data = request.json

    try:
        # 1. Verifica se é uma mensagem válida (ignora status de entrega)
        value = data.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {})
        if "messages" not in value:
            return "ok", 200

        message = value["messages"][0]
        user_number = message["from"]

        # 2. Lógica para quando o usuário seleciona um item da LISTA
        if message["type"] == "interactive" and message["interactive"]["type"] == "list_reply":
            escolha_id = message["interactive"]["list_reply"]["id"]
            
            if escolha_id in SETORES:
                setor, telefone = SETORES[escolha_id]
                resposta = (
                    f"✅ *Setor selecionado:* {setor}\n\n"
                    f"Para prosseguir com seu atendimento, entre em contato pelo número:\n"
                    f"{telefone}"
                )
                enviar_mensagem_texto(user_number, resposta)
            else:
                enviar_menu_lista(user_number)

        # 3. Lógica para quando o usuário manda um TEXTO comum (ex: "Oi")
        elif message["type"] == "text":
            # Qualquer texto enviado dispara o menu de lista
            enviar_menu_lista(user_number)

    except Exception as e:
        print(f"Erro ao processar: {e}")

    return "ok", 200

if __name__ == "__main__":
    # Em produção com Gunicorn, este bloco não é usado, mas mantemos para testes locais
    app.run(host="0.0.0.0", port=5000)
