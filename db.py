from pony.orm import *
from datetime import datetime

db = Database()


class User(db.Entity):
    discord_id = PrimaryKey(int, size=64)
    vk_id = Optional(int)
    token = Required(str)
    incoming_alerts = Set('Alert', reverse='user_to')
    outgoing_alerts = Set('Alert', reverse='user_from')


class Alert(db.Entity):
    user_from = Required(User, reverse='outgoing_alerts')
    user_to = Required(User, reverse='incoming_alerts')
    via = Required(str)  # social network
    dt = Required(datetime)