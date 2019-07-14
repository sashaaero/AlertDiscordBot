from http.server import BaseHTTPRequestHandler, HTTPServer
import json, logging, vk
from config import settings
from db import db, User, db_session


class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    @db_session
    def do_POST(self):
        if self.path.startswith(settings['vk_handler_path']):
            content_len = int(self.headers.get('Content-Length'))
            data = json.loads(self.rfile.read(content_len))
            print(data)
            if "type" in data:
                if data['type'] == 'confirmation':
                    self._set_response()
                    self.wfile.write(bytes(settings['vk_confirmation_code'], "utf-8"))
                elif data['type'] == 'message_new':
                    user_id = data['object']['from_id']
                    message = data['object']['text']

                    user = User.get(token=message)
                    if user:
                        if not user.vk_id:
                            user.vk_id = user_id
                            api.messages.send(user_id=user_id, message="Активация прошла успешно",
                                          v=settings['vk_api_version'])
                        else:
                            api.messages.send(user_id=user_id, message="Вы уже привязали страницу ранее",
                                              v=settings['vk_api_version'])

def run_http_server(server_class=HTTPServer, handler_class=S, port=80):
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
    session = vk.Session(access_token=settings['vk_token'])
    api = vk.API(session)
    run_http_server()
