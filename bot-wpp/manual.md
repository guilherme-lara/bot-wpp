# 📘 Manual de Implantação: Bot WhatsApp Business API

**Versão:** 1.0

**Ambiente:** Produção (VM Linux/Ubuntu)

**Stack:** Python, Flask, Gunicorn, Nginx, Systemd

---

## 1. Preparação do Servidor (VM)

Acesse sua VM via SSH e execute os comandos para atualizar o sistema e instalar as dependências básicas.

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv nginx git -y

```

---

## 2. Organização do Projeto

Recomenda-se manter o projeto em um diretório específico para facilitar a gestão de permissões.

```bash
mkdir ~/whatsapp-bot && cd ~/whatsapp-bot
python3 -m venv venv
source venv/bin/activate
pip install flask requests python-dotenv gunicorn

```

### Criando o arquivo .env

Crie o arquivo para armazenar suas credenciais sensíveis:
`nano .env`

```env
VERIFY_TOKEN="seu_token_de_verificacao"
ACCESS_TOKEN="seu_token_da_meta"
PHONE_NUMBER_ID="seu_id_do_numero"

```

---

## 3. Configuração do Servidor de Aplicação (Gunicorn)

O Gunicorn servirá sua aplicação Flask de forma robusta. Para garantir que ele rode 24/7, criaremos um serviço no Linux.

### Criar o serviço do sistema:

`sudo nano /etc/systemd/system/whatsapp-bot.service`

**Cole o seguinte conteúdo (ajuste o nome de usuário):**

```ini
[Unit]
Description=Gunicorn instance to serve WhatsApp Bot
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/root/whatsapp-bot
Environment="PATH=/root/whatsapp-bot/venv/bin"
ExecStart=/root/whatsapp-bot/venv/bin/gunicorn --workers 3 --bind unix:app.sock app:app
Restart=always

[Install]
WantedBy=multi-user.target

```

### Iniciar o serviço:

```bash
sudo systemctl daemon-reload
sudo systemctl start whatsapp-bot
sudo systemctl enable whatsapp-bot

```

---

## 4. Configuração do Proxy Reverso (Nginx)

O Nginx receberá as requisições na porta 80 (HTTP) e as enviará para o seu bot.

### Criar configuração do Nginx:

`sudo nano /etc/nginx/sites-available/whatsapp-bot`

**Conteúdo:**

```nginx
server {
    listen 80;
    server_name seu_dominio_ou_ip;

    location / {
        include proxy_params;
        proxy_pass http://unix:/root/whatsapp-bot/app.sock;
    }
}

```

### Ativar o site e reiniciar o Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/whatsapp-bot /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx

```

---

## 5. Segurança (SSL/HTTPS) - OBRIGATÓRIO

A Meta exige que o Webhook seja **HTTPS**. Use o Certbot para gerar um certificado gratuito.

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d seu_dominio.com

```

---

## 6. Configuração no Painel Meta (Facebook)

1. **Callback URL:** `https://seu_dominio.com/webhook`
2. **Verify Token:** O mesmo que você definiu no seu `.env`.
3. **Webhooks Fields:** Clique em "Manage" e assine a opção **messages**.

---

## 7. Comandos de Manutenção Úteis

| Ação | Comando |
| --- | --- |
| **Ver Logs do Bot** | `sudo journalctl -u whatsapp-bot -f` |
| **Reiniciar o Bot** | `sudo systemctl restart whatsapp-bot` |
| **Ver Status do Bot** | `sudo systemctl status whatsapp-bot` |
| **Ver Erros do Nginx** | `sudo tail -f /var/log/nginx/error.log` |

---

