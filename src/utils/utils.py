from typing import Literal
import src.utils.cache as cache

default_prefixes = ['K.', 'k.']


def printc(color: Literal["green", "yellow", "blue", "red"], text: str):
    colors = {
        "green": f"\033[1;32;48m{text}\033[1;37;0m",
        "yellow": f"\033[1;33;48m{text}\033[1;37;0m",
        "blue": f"\033[1;34;48m{text}\033[1;37;0m",
        "red": f"\033[1;31;48m{text}\033[1;37;0m",
    }

    print(colors[color])


async def get_user_audit(guild, action):
    e = await guild.audit_logs(limit=1, action=action).get()
    return e.user


async def determine_prefix(bot, message):
    if message.guild:
        try:
            return cache.configs_data[message.guild.id]["prefix"]
        except KeyError:
            return default_prefixes
