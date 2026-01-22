1. Criar o Arquivo de Serviço (Systemd)
Comando: sudo nano /etc/systemd/system/loe-bot.service

Conteúdo atualizado:

Ini, TOML

[Unit]
Description=Gunicorn instance to serve LOE Construtora WhatsApp Bot
After=network.target

[Service]
User=root
Group=www-data
# Caminho atualizado para a sua pasta
WorkingDirectory=/root/bot-wpp
Environment="PATH=/root/bot-wpp/venv/bin"
# Executando o Gunicorn
ExecStart=/root/bot-wpp/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
2. Configuração do Nginx
Comando: sudo nano /etc/nginx/sites-available/loe-bot

Conteúdo:

Nginx

server {
    listen 80;
    server_name wpp.loeconstrutora.com.br;

    location / {
        include proxy_params;
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
🚀 Comandos para o Deploy Final
Assim que o TI confirmar o DNS e o Firewall, execute esta sequência:

Ativar o Nginx:

Bash

sudo ln -s /etc/nginx/sites-available/loe-bot /etc/nginx/sites-enabled
sudo nginx -t && sudo systemctl restart nginx
Gerar o SSL (HTTPS):

Bash

sudo certbot --nginx -d wpp.loeconstrutora.com.br
Iniciar o Bot:

Bash

sudo systemctl daemon-reload
sudo systemctl enable loe-bot
sudo systemctl start loe-bot
Como verificar se está tudo certo?
Para ver se o bot subiu sem erros, use: sudo systemctl status loe-bot

Se precisar ver as mensagens que o bot está processando em tempo real: sudo journalctl -u loe-bot -f
