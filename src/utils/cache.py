from ..mongo import db
import asyncio


class Collection:
    def __init__(self, collection):
        self.collection = db[collection]
        print(collection, "loaded")
        self.cached = {}

    async def add(self, _id, data):
        idict = {"_id": _id}
        await self.collection.update_one(idict, {"$set": data}, upsert=True)
        if _id not in self.cached:
            self.cached[_id] = {}
        for i in data:
            self.cached[_id][i] = data[i]

    async def remove(self, ids):
        idict = {"_id": ids}
        await self.collection.delete_one(idict)
        del self.cached[ids]

    async def delete(self, _id, data):
        idict = {"_id": _id}
        await self.collection.update_one(idict, {"$unset": data})
        for i in data:
            del self.cached[_id][i]

    async def load_data(self):
        results = self.collection.find({})
        async for res in results:
            self.cached[res["_id"]] = res
        return self.cached

asyncio.set_event_loop(asyncio.new_event_loop())
loop = asyncio.get_event_loop()
configs = Collection(collection = "config")
configs_data = loop.run_until_complete(configs.load_data())
print(configs_data)
loop.close()

antiflood = Collection(collection = "antiflood")
antiflood_data = loop.run_until_complete(antiflood.load_data())
loop.close()

antiinvite = Collection(collection = "antiinvite")
antiinvite_data = loop.run_until_complete(antiinvite.load_data())
loop.close()

antiraid = Collection(collection = "antiraid")
antiraid_data = loop.run_until_complete(antiraid.load_data())
loop.close()

bans = Collection(collection = "bans")
bans_data = loop.run_until_complete(bans.load_data())
loop.close()

locks = Collection(collection = "locks")
locks_data = loop.run_until_complete(locks.load_data())
loop.close()

mutes = Collection(collection = "mutes")
mutes_data = loop.run_until_complete(mutes.load_data())

warns = Collection(collection = "warns")
warns_data = loop.run_until_complete(warns.load_data())

invited = Collection(collection = "invited")
invited_data = loop.run_until_complete(invited.load_data())

perms = Collection(collection = "perms")
perms_data = perms.load_data()

rr = Collection(collection = "rr-new")
rr_data = rr.load_data()

whitelist = Collection(collection = "whitelist")
whitelist_data = whitelist.load_data()

quarantine = Collection(collection = "quarantine")
quarantine_data = quarantine.load_data()

bl = Collection(collection = "bot-bl")
bl_data = bl.load_data()

logs = Collection(collection = "logs")
logs_data = logs.load_data()

bonus = Collection(collection = "bonus")
bonus_data = bonus.load_data()

antinuke = Collection(collection = "antinuke")
antinuke_data = antinuke.load_data()

botstats = Collection(collection = "bot_stats")
botstats_data = botstats.load_data()

premium = Collection(collection = "premium")
premium_data = premium.load_data()

invoices = Collection(collection = "invoices")
invoices_data = invoices.load_data()

allowed = Collection(collection = "allowed")
allowed_data = allowed.load_data()

auto = Collection(collection = "auto")
auto_data = auto.load_data()

report = Collection(collection = "report")
report_data = report.load_data()

welcome = Collection(collection = "welcome")
welcome_data = welcome.load_data()