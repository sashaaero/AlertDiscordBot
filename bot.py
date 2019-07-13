import vk_api as vk, discord
from config import settings
from urllib import parse
import asyncio
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import requests


def main():
    pass


def parse_url():
    params = parse.urlencode(settings['vk_redirect'])
    return f"https://oauth.vk.com/authorize?{params}"

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

    def do_GET(self):
        if self.path.startswith('/vk_handle'):
            print("query")
            params = parse.parse_qs(parse.urlparse(self.path).query)
            code = params['code'][0]
            user_id = get_user_by_code(code)
            # TODO save VK_ID to db

class DiscordClient(discord.Client):
    prefix = settings['bot_prefix']

    @staticmethod
    async def on_ready():
        print('Logged')

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith(self.prefix):
            text = message.content[len(self.prefix):]
            command = text.split()[0]
            if command == "vk":
                await message.author.send(parse_url())
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
    run()
    client = DiscordClient()
    client.run('MzExMzU4NTMyNjMwODcyMDY0.XSj-6Q.-rmaXBO4vjXmcaABk_p7-g1ZqnU')
