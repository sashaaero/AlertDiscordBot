import vk, discord, logging, requests, string, random, asyncio, json, re, datetime
from config import settings
from urllib import parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from db import db, User, db_session, Alert, select, desc


def generate_token(len=32):
    alphabet = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.choice(alphabet) for _ in range(len))


def get_user_by_code(code):
    URL = "https://oauth.vk.com/access_token"
    PARAMS = settings['vk_settings']
    PARAMS['code'] = code
    r = requests.get(url=URL, params=PARAMS)
    data = r.json()
    user_id = data.get('user_id', 0)
    return user_id


class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    @db_session
    def do_POST(self):
        if self.path.startswith('/vk_handle'):
            content_len = int(self.headers.get('Content-Length'))
            data = json.loads(self.rfile.read(content_len))
            if "type" in data:
                if data['type'] == 'confirmation':
                    self._set_response()
                    self.wfile.write("ec44f68f")
                elif data['type'] == 'message_new':
                    user_id = data['object']['from_id']
                    message = data['object']['text']

                    user = User.get(token=message)
                    if user:
                        user.vk_id = user_id


class DiscordClient(discord.Client):
    prefix = settings['bot_prefix']

    @staticmethod
    def send_message_vk(vk_id, author, channel):
        message = settings['alert_vk_message'].format({
            'username': author, 'servername': channel.guild, 'channel': channel,
            'server_id': channel.guild.id, 'channel_id': channel.id
        })
        api.messages.send(user_id=vk_id, message=message, v=5.38)
        # 319954540

    @staticmethod
    async def on_ready():
        print('Logged')

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith(self.prefix):
            text = message.content[len(self.prefix):]
            command, *args = text.split()

            if command == "auth":
                if len(args) == 1 and args[0] == "vk":
                    with db_session:
                        user = User.get(discord_id=message.author.id)
                    if not user:
                        with db_session:
                            user = User(discord_id=message.author.id, token=generate_token())

                    await message.channel.send(
                        f'Отправь мне токен {user.token} в лс тут: {settings["vk_link"]}')
                else:
                    message.channel.send('anonist')  # todo show help
            if command == "alert":
                if len(args) == 2 and args[0] == "vk":
                    discord_id = re.sub("\D", "", args[1])
                    with db_session:
                        user_to = User[discord_id]
                    if user_to and user_to.vk_id:
                        # get last alert
                        user_from = User[message.author.id]
                        last_alert = select(a for a in Alert if a.user_from == user_from and a.user_to == user_to)
                        last_alert = last_alert.order_by(lambda a: a.dt, desc).limit(1)
                        now = datetime.datetime.now()
                        if last_alert:
                            if now - last_alert < settings['alert_vk_timeout']:
                                message.channel.send(settings['alert_vk_timeout_error_message'])
                                return
                        self.send_message_vk(user_to.vk_id, message.author.name, message.channel)
                        Alert(user_from=user_from, user_to=user_to, via='vk', dt=now)
                    else:
                        message.channel.send('Пользователь не привязал свою страницу VK')
            else:
                pass
                # await message.channel.send('')


def run(server_class=HTTPServer, handler_class=S, port=8000):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')


if __name__ == '__main__':
    db.bind(**settings['db'])
    db.generate_mapping(create_tables=True)
    # run()
    session = vk.Session(access_token=settings['vk_token'])
    api = vk.API(session)

    client = DiscordClient()
    client.run('MzExMzU4NTMyNjMwODcyMDY0.XSj-6Q.-rmaXBO4vjXmcaABk_p7-g1ZqnU')
