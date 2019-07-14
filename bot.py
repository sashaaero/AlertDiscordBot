import vk, discord, logging, requests, string, random, asyncio, json, re, datetime
from config import settings
from urllib import parse
from db import db, User, db_session, Alert, select, desc


def generate_token(len=32):
    alphabet = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.choice(alphabet) for _ in range(len))


class DiscordClient(discord.Client):
    prefix = settings['bot_prefix']

    @staticmethod
    def send_message_vk(vk_id, author, channel):
        message = settings['alert_vk_message'].format(**{
            'username': author, 'servername': channel.guild, 'channel': channel,
            'server_id': channel.guild.id, 'channel_id': channel.id
        })
        api.messages.send(user_id=vk_id, message=message, v=settings['vk_api_version'])
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
                    # todo validate duplicate requests
                    with db_session:
                        user = User.get(discord_id=message.author.id)
                    if not user:
                        with db_session:
                            user = User(discord_id=message.author.id, token=generate_token())
                            vk_id = user.vk_id
                    if vk_id:
                        await message.author.send(
                            'Вы уже привязали свою страницу VK')
                    else:
                        await message.author.send(
                            f'Отправь мне токен {user.token} в лс тут: {settings["vk_link"]}')
                else:
                    message.channel.send('anonist')  # todo show help
            if command == "alert":
                if len(args) == 2 and args[0] == "vk":
                    discord_id = re.sub("\D", "", args[1])
                    with db_session:
                        user_to = User.get(discord_id=discord_id)
                    if user_to and user_to.vk_id:
                        # get last alert
                        with db_session:
                            user_from = User[message.author.id]
                            last_alert = select(a for a in Alert if a.user_from == user_from and
                                                a.user_to.discord_id == user_to.discord_id)
                            last_alert = last_alert.order_by(lambda a: desc(a.dt)).limit(1)[:]
                        now = datetime.datetime.now()
                        if last_alert:
                            if (now - last_alert[0].dt).seconds < settings['alert_vk_timeout']:
                                await message.channel.send(settings['alert_vk_timeout_error_message'])
                                return
                        self.send_message_vk(user_to.vk_id, message.author.name, message.channel)
                        with db_session:
                            Alert(user_from=User[message.author.id], user_to=User[discord_id], via='vk', dt=now)
                    else:
                        await message.channel.send('Пользователь не привязал свою страницу VK')
            else:
                pass
                # await message.channel.send('')


if __name__ == '__main__':
    db.bind(**settings['db'])
    db.generate_mapping(create_tables=True)
    session = vk.Session(access_token=settings['vk_token'])
    api = vk.API(session)
    client = DiscordClient()
    client.run('MzExMzU4NTMyNjMwODcyMDY0.XSj-6Q.-rmaXBO4vjXmcaABk_p7-g1ZqnU')
