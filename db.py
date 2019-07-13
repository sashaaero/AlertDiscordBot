from pony.orm import *
from config import settings
from datetime import datetime

db = Database()


class User(db.Entity):
    discord_id = PrimaryKey(int, size=64)
    vk_id = Optional(int)
    token = Required(str)
    last_alert = Optional(datetime)