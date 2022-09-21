from distutils.log import debug
from src.bot import BotClass
import config

bot = BotClass()

if config.Other.debug:
    bot.run(config.Auth.discord_auth.get("debug"))
else:
    bot.run(config.Auth.discord_auth.get("release"))
