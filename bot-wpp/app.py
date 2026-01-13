import os
import requests
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

SETORES = {
    "1": ("Financeiro", "+55 11 99999-1111"),
    "2": ("Projetos", "+55 11 99999-2222"),
    "3": ("RH", "+55 11 99999-3333"),
}

MENU = (
    "Olá! 👋 Seja bem-vindo.\n\n"
    "Por favor, escolha o setor desejado:\n"
    "1️⃣ Financeiro\n"
    "2️⃣ Projetos\n"
    "3️⃣ RH\n\n"
    "Responda apenas com o número."
)


# 🔎 Verificação do Webhook (Meta)
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200

    return "Erro de verificação", 403


# 📩 Recebimento de mensagens
@app.route("/webhook", methods=["POST"])
def receive_message():
    data = request.json
    
    # Ignora notificações de status (lido, entregue, enviado)
    if "messages" not in data.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {}):
        return "ok", 200

    try:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]
        if message["type"] == "text":
            user_number = message["from"]
            text = message["text"]["body"].strip()
            
            resposta = gerar_resposta(text)
            enviar_mensagem(user_number, resposta)
    except Exception as e:
        print(f"Erro ao processar: {e}")

    return "ok", 200


def gerar_resposta(texto):
    if texto not in SETORES:
        return MENU

    setor, telefone = SETORES[texto]
    return (
        f"✅ *Setor selecionado:* {setor}\n\n"
        f"Entre em contato pelo número:\n"
        f"{telefone}"
    )


def enviar_mensagem(numero, texto):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": numero,
        "text": {
            "body": texto
        }
    }

    requests.post(url, headers=headers, json=payload)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
