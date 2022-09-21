from cache import bonus_data


async def is_owner(ctx):
    if ctx.author.id not in [889918463546650644]:
        await ctx.send("Эта команда доступна только владельцам бота!")
        return False
    return True


def get_bonus_data(user_id, nostr=False):
    dict_ = {
        "balance": 0.0,
        "pay-period": 0,
        "guilds": [],
    }
    if not nostr:
        dict_["strbal"] = "0.00"
    if user_id not in bonus_data:
        return dict_

    data = bonus_data[user_id]
    print(bonus_data)

    if "balance" in data:
        dict_["balance"] = data["balance"]
    if "pay-period" in data:
        dict_["pay-period"] = data["pay-period"]
    if "guilds" in data:
        dict_["guilds"] = data["guilds"]
    if not nostr:
        dict_["strbal"] = "{:.2f}".format(dict_["balance"])

    return dict_
