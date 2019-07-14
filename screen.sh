screen -X -S discord-bot kill
screen -X -S http_server kill
screen -AdmS discord-bot python3 bot.py
screen -AdmS http_server python3 http_server.py