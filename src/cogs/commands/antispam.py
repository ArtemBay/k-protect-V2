import discord
from discord.ext import commands
from config import Color
import messages
import word
import punishments
import asyncio
import mongo
import time
import datetime
import typing
import random
import cache
from word import ago
from discord.utils import get
from profilactic import measures


def spamer(ctx, mode):
    ir, ic = [], []
    enabled = False
    if mode == 'antiflood': c = cache.antiflood_data
    else: c = cache.antiinvite_data
    if ctx.guild.id in c:
        v = c[ctx.guild.id]
        try:
            ir = v['ir']
        except:
            pass
        try:
            ic = v['ic']
        except:
            pass
        try:
            enabled = v['enabled']
        except:
            pass
        
    oneofrole = False
    for i in ir:
        if ctx.guild.get_role(int(i)) in ctx.author.roles:
            oneofrole = True
    return not ctx.channel.id in ic and not oneofrole and ctx.author != ctx.guild.owner and enabled

msgs = {}
async def clear_af(guild, user):
    await asyncio.sleep(60)
    global msgs
    try:
        del msgs[guild.id][user.id]
        if len(list(msgs[guild.id])) == 0:
            del msgs[guild.id]
    except:
        pass

class AntiSpam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Команды
    @commands.group(aliases=['ai'])
    @commands.check(messages.check_perms)
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def antiinvite(self, ctx):
        measures.add(what=7)
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(title = "⚡ | Анти-ссылки-приглашения")
            embed.color = Color.success
            p = ctx.prefix
            embed.description = f'''
`<обязательный параметр>` `[необязательный параметр]`
**Не используйте скобочки при указании параметров.**

`{p}antiinvite <on | off>` – переключить защиту от ссылок
`{p}antiinvite punishment <none | warn | mute | kick | ban> [длительность]` – установить наказание
`{p}antiinvite ir <роли>` – установить игнорируемые роли
`{p}antiinvite ic <каналы>` – установить игнорируемые каналы
            '''
            with ctx.channel.typing():
                if ctx.guild.id in cache.antiinvite_data:
                    v = cache.antiinvite_data[ctx.guild.id]
                    ir, ic = "", ""
                    cpunishments = {"none": "Отсутствует", "warn": "Предупреждение", "mute": "Мьют", "kick": "Кик", "ban": "Бан"}
                    temp = ""
                    try:
                        for i in v['ir']:
                            try:
                                r = ctx.guild.get_role(int(i))
                                ir += f'{r.mention} '
                            except:
                                pass
                        if not len(ir.split()): ir = "Отсутствуют"
                    except KeyError:
                        ir = "Отсутствуют"
                    try:
                        for i in v['ic']:
                            try:
                                c = self.bot.get_channel(int(i))
                                ic += f'{c.mention} '
                            except:
                                pass
                        try:
                            if not len(iс.split()): iс = "Отсутствуют"
                        except:
                            pass
                        try:
                            if ic == "": ic = "Отсутствуют"
                        except:
                            pass
                    except KeyError:
                        ic = "Отсутствуют"
                    try:
                        if v['punishment']['duration'] > 0:
                            temp = f" на {word.hms2(v['punishment']['duration'])}"
                    except:
                        pass
                    try:
                        punishment = cpunishments[v['punishment']['type']]
                    except KeyError:
                        punishment = "Отсутствует"

                    try:
                        if v['enabled']:
                            enabled = "Включено"
                        else:
                            enabled = "Выключено"
                    except KeyError:
                        enabled = "Выключено"
                else:
                    ir, ic = "Отсутствуют", "Отсутствуют"
                    enabled = "Выключено"
                    punishment = "Отсутствует"
                    temp = ""

                embed.add_field(
                    name = "Настройки",
                    value = f"""
**Игнорируемые роли:** {ir}
**Игнорируемые каналы:** {ic}
**Наказание:** {punishment}{temp}
**Состояние:** {enabled}
                    """
                )
                await ctx.send(embed = embed)

    @antiinvite.command(aliases = ['ignorechannels', 'ignore_channels'])
    async def ic(self, ctx, channels: commands.Greedy[discord.TextChannel]):
        with ctx.channel.typing():
            if not ctx.guild.id in cache.antiinvite_data:
                cache.antiinvite_data[ctx.guild.id] = {}
            try:
                data = cache.antiinvite_data[ctx.guild.id]
            except KeyError:
                data = {}
            data['ic'] = [ch.id for ch in channels]
            cache.antiinvite.add(ctx.guild.id, data)
            embed = discord.Embed(color = Color.success)
            embed.title = "✅ | Готово"
            if len(channels):
                embed.description = f'Игнорируемые каналы были установлены на {", ".join(c.mention for c in channels)}.'
            else:
                embed.description = f'Игнорируемые каналы были сброшены.'
            await ctx.send(embed = embed)

    @antiinvite.command(aliases = ['ignoreroles', 'ignore_roles'])
    async def ir(self, ctx, roles: commands.Greedy[discord.Role]):
        with ctx.channel.typing():
            if not ctx.guild.id in cache.antiinvite_data:
                cache.antiinvite_data[ctx.guild.id] = {}
            try:
                data = cache.antiinvite_data[ctx.guild.id]
            except KeyError:
                data = {}
            data['ir'] = [ch.id for ch in roles]
            cache.antiinvite.add(ctx.guild.id, data)
            embed = discord.Embed(color = Color.success)
            embed.title = "✅ | Готово"
            if len(roles):
                embed.description = f'Игнорируемые роли были установлены на {", ".join(c.mention for c in roles)}.'
            else: embed.description = 'Игнорируемые роли были сброшены.'
            await ctx.send(embed = embed)

    @antiinvite.command(aliases = ['pm'])
    async def punishment(self, ctx, p, t = "0s"):
        with ctx.channel.typing():
            p = p.lower()
            ct = word.string_to_seconds(t)
            cpunishments = {"none": "Ничего", "warn": "Предупреждение", "mute": "Мьют", "kick": "Кик", "ban": "Бан"}
            temp = ""
            if not ctx.guild.id in cache.antiinvite_data:
                cache.antiinvite_data[ctx.guild.id] = {}
            try:
                data = cache.antiinvite_data[ctx.guild.id]
            except KeyError:
                data = {}
            if ct > 0:
                temp = f" на {word.hms2(ct)}"

            if ct > 0 and p in ['none', 'warn', 'kick']:
                await messages.err(ctx, f"{cpunishments[p]} не имеет настройки по времени.", True)
            else:
                data['punishment'] = {}
                data['punishment']['type'] = p
                data['punishment']['duration'] = ct
                cache.antiinvite.add(ctx.guild.id, data)
                embed = discord.Embed(color = Color.success)
                embed.title = "✅ | Готово"
                embed.description = f'Теперь отправивший ссылку-приглашение получит {cpunishments[p].lower()}{temp}.'
                await ctx.send(embed = embed)

    @antiinvite.command(aliases = ['on'])
    async def _on(self, ctx):
        with ctx.channel.typing():
            if not ctx.guild.id in cache.antiinvite_data:
                cache.antiinvite_data[ctx.guild.id] = {}
            try:
                data = cache.antiinvite_data[ctx.guild.id]
            except KeyError:
                data = {}

            try:
                en = data['enabled']
            except:
                en = False

            if en:
                await messages.err(ctx, "Фильтр уже включён.", True)
            else:
                data['enabled'] = True
                cache.antiinvite.add(ctx.guild.id, data)
                embed = discord.Embed(color = Color.success)
                embed.title = "✅ | Готово"
                embed.description = 'Фильтр ссылок-приглашений включён. Наслаждайтесь ;)'
                await ctx.send(embed = embed)

    @antiinvite.command(aliases = ['off'])
    async def _off(self, ctx):
        with ctx.channel.typing():
            if not ctx.guild.id in cache.antiinvite_data:
                cache.antiinvite_data[ctx.guild.id] = {}
            try:
                data = cache.antiinvite_data[ctx.guild.id]
            except KeyError:
                data = {}

            try:
                en = data['enabled']
            except:
                en = False

            if not en:
                await messages.err(ctx, "Фильтр уже выключен.", True)
            else:
                data['enabled'] = False
                cache.antiinvite.add(ctx.guild.id, data)
                embed = discord.Embed(color = Color.success)
                embed.title = "✅ | Готово"
                embed.description = 'Фильтр ссылок-приглашений был выключен.'
                await ctx.send(embed = embed)


    @commands.group(aliases=['af'])
    @commands.check(messages.check_perms)
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def antiflood(self, ctx):
        measures.add(what=7)
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(title = "☁️ | Анти-флуд")
            embed.color = Color.success
            p = ctx.prefix
            embed.description = f'''
`<обязательный параметр>` `[необязательный параметр]`
**Не используйте скобочки при указании параметров.**

`{p}antiflood <on | off>` – переключить защиту от флуда
`{p}antiflood punishment <none | warn | mute | kick | ban> [длительность]` – установить наказание
`{p}antiflood ir <роли>` – установить игнорируемые роли
`{p}antiflood ic <каналы>` – установить игнорируемые каналы
`{p}antiflood maxmsg <кол-во сообщений>` – установить максимальное количество повторяющихся сообщений
            '''
            with ctx.channel.typing():
                if ctx.guild.id in cache.antiflood_data:
                    v = cache.antiflood_data[ctx.guild.id]
                    ir, ic = "", ""
                    cpunishments = {"none": "Отсутствует", "warn": "Предупреждение", "mute": "Мьют", "kick": "Кик", "ban": "Бан"}
                    temp = ""
                    try:
                        for i in v['ir']:
                            try:
                                r = ctx.guild.get_role(int(i))
                                ir += f'{r.mention} '
                            except:
                                pass
                        if not len(ir.split()): ir = "Отсутствуют"
                    except KeyError:
                        ir = "Отсутствуют"
                    try:
                        for i in v['ic']:
                            try:
                                c = self.bot.get_channel(int(i))
                                ic += f'{c.mention} '
                            except:
                                pass
                        try:
                            if not len(iс.split()): iс = "Отсутствуют"
                        except:
                            pass
                        try:
                            if ic == "": ic = "Отсутствуют"
                        except:
                            pass
                    except KeyError:
                        ic = "Отсутствуют"
                    try:
                        if v['punishment']['duration'] > 0:
                            temp = f" на {word.hms2(v['punishment']['duration'])}"
                    except:
                        pass
                    try:
                        punishment = cpunishments[v['punishment']['type']]
                    except KeyError:
                        punishment = "Отсутствует"

                    try:
                        maxmsg = v['max']
                    except KeyError:
                        maxmsg = 3

                    try:
                        if v['enabled']:
                            enabled = "Включено"
                        else:
                            enabled = "Выключено"
                    except KeyError:
                        enabled = "Выключено"
                else:
                    ir, ic = "Отсутствуют", "Отсутствуют"
                    enabled = "Выключено"
                    punishment = "Отсутствует"
                    temp = ""
                    maxmsg = 3 

                embed.add_field(
                    name = "Настройки",
                    value = f"""
**Игнорируемые роли:** {ir}
**Игнорируемые каналы:** {ic}
**Наказание:** {punishment}{temp}
**Состояние:** {enabled}
**Максимум сообщений:** {maxmsg}
                    """
                )
                await ctx.send(embed = embed)

    @antiflood.command(aliases = ['ic', 'ignorechannels', 'ignore_channels'])
    async def _ic(self, ctx, channels: commands.Greedy[discord.TextChannel]):
        with ctx.channel.typing():
            if not ctx.guild.id in cache.antiflood_data:
                cache.antiflood_data[ctx.guild.id] = {}
            try:
                data = cache.antiflood_data[ctx.guild.id]
            except KeyError:
                data = {}
            data['ic'] = [ch.id for ch in channels]
            cache.antiflood.add(ctx.guild.id, data)
            embed = discord.Embed(color = Color.success)
            embed.title = "✅ | Готово"
            if len(channels):
                embed.description = f'Игнорируемые каналы были установлены на {", ".join(c.mention for c in channels)}.'
            else:
                embed.description = 'Игнорируемые каналы были сброшены.'
            await ctx.send(embed = embed)

    @antiflood.command(aliases = ['ir', 'ignoreroles', 'ignore_roles'])
    async def _ir(self, ctx, roles: commands.Greedy[discord.Role]):
        with ctx.channel.typing():
            if not ctx.guild.id in cache.antiflood_data:
                cache.antiflood_data[ctx.guild.id] = {}
            try:
                data = cache.antiflood_data[ctx.guild.id]
            except KeyError:
                data = {}
            data['ir'] = [ch.id for ch in roles]
            cache.antiflood.add(ctx.guild.id, data)
            embed = discord.Embed(color = Color.success)
            embed.title = "✅ | Готово"
            if len(roles):
                embed.description = f'Игнорируемые роли были установлены на {", ".join(c.mention for c in roles)}.'
            else:
                embed.description = 'Игнорируемые роли были сброшены.'
            await ctx.send(embed = embed)

    @antiflood.command(aliases = ['pm', 'punishment'])
    async def _punishment(self, ctx, p, t = "0s"):
        with ctx.channel.typing():
            p = p.lower()
            ct = word.string_to_seconds(t)
            cpunishments = {"none": "Ничего", "warn": "Предупреждение", "mute": "Мьют", "kick": "Кик", "ban": "Бан"}
            temp = ""
            if not ctx.guild.id in cache.antiflood_data:
                cache.antiflood_data[ctx.guild.id] = {}
            try:
                data = cache.antiflood_data[ctx.guild.id]
            except KeyError:
                data = {}
            if ct > 0:
                temp = f" на {word.hms2(ct)}"

            if ct > 0 and p in ['none', 'warn', 'kick']:
                await messages.err(ctx, f"{cpunishments[p]} не имеет настройки по времени.", True)
            else:
                data['punishment'] = {}
                data['punishment']['type'] = p
                data['punishment']['duration'] = ct
                cache.antiflood.add(ctx.guild.id, data)
                embed = discord.Embed(color = Color.success)
                embed.title = "✅ | Готово"
                embed.description = f'Теперь флудер получит {cpunishments[p].lower()}{temp}.'
                await ctx.send(embed = embed)

    @antiflood.command(aliases = ['on'])
    async def __on(self, ctx):
        with ctx.channel.typing():
            if not ctx.guild.id in cache.antiflood_data:
                cache.antiflood_data[ctx.guild.id] = {}
            try:
                data = cache.antiflood_data[ctx.guild.id]
            except KeyError:
                data = {}

            try:
                en = data['enabled']
            except:
                en = False

            if en:
                await messages.err(ctx, "Фильтр уже включён.", True)
            else:
                data['enabled'] = True
                cache.antiflood.add(ctx.guild.id, data)
                embed = discord.Embed(color = Color.success)
                embed.title = "✅ | Готово"
                embed.description = 'Фильтр от флуда включён. Наслаждайтесь ;)'
                await ctx.send(embed = embed)

    @antiflood.command(aliases = ['off'])
    async def __off(self, ctx):
        with ctx.channel.typing():
            if not ctx.guild.id in cache.antiflood_data:
                cache.antiflood_data[ctx.guild.id] = {}
            try:
                data = cache.antiflood_data[ctx.guild.id]
            except KeyError:
                data = {}
            
            try:
                en = data['enabled']
            except:
                en = False

            if not en:
                await messages.err(ctx, "Фильтр уже выключен.", True)
            else:
                data['enabled'] = False
                cache.antiflood.add(ctx.guild.id, data)
                embed = discord.Embed(color = Color.success)
                embed.title = "✅ | Готово"
                embed.description = 'Фильтр от флуда был выключен.'
                await ctx.send(embed = embed)

    @antiflood.command(aliases = ['mm', 'max'])
    async def maxmsg(self, ctx, amount: int):
        with ctx.channel.typing():
            if not ctx.guild.id in cache.antiflood_data:
                cache.antiflood_data[ctx.guild.id] = {}
            try:
                data = cache.antiflood_data[ctx.guild.id]
            except KeyError:
                data = {}
            if amount < 1:
                await messages.err(ctx, "Минимум - 1 сообщение.", True)
            else:
                data['max'] = amount
                cache.antiflood.add(ctx.guild.id, data)
                embed = discord.Embed(color = Color.success)
                embed.title = "✅ | Готово"
                embed.description = f'Максимальное количество повторяющихся сообщений: **{amount}**.'
                await ctx.send(embed = embed)

    '''@commands.Cog.listener()
    async def on_message(self, msg):
        global msgs
        if not msg.author.bot:
            if word.oneof(msg.content, ['discord.gg/', 'discord.com/invite/', 'discordapp.com/invite/', 'dsc.gg/'])[0]:
                if spamer(msg, 'antiinvite'):
                    measures.add(what=8)
                    await msg.delete()
                    await msg.channel.send(f'{msg.author.mention}, здесь запрещено оставлять ссылки-приглашения.', delete_after = 10.0)
                    try: v = cache.antiinvite_data[msg.guild.id]
                    except: v = {}
                    try:
                        pdict = v['punishment']
                    except:
                        pdict = {"type": "none", "duration": 0}
                    if pdict['duration'] == 0:
                        pdict['duration'] = 228133722
                    if pdict['type'] == 'mute':
                        await punishments.tempmute(msg, msg.author, pdict['duration'])
                    elif pdict['type'] == 'warn':
                        await punishments.warn(msg, msg.author)
                    elif pdict['type'] == 'kick':
                        await msg.author.kick(reason = "Анти-ссылки-приглашения")
                    elif pdict['type'] == 'ban':
                        if pdict['duration'] == 228133722:
                            await msg.author.ban(reason = "Анти-ссылки-приглашения")
                        else:
                            await msg.author.ban(reason = f"Анти-ссылки-приглашения | {word.hms(pdict['duration'])}")
                        await punishments.tempban(msg, msg.author, pdict['duration'])
              if not msg.guild.id in msgs:
                msgs[msg.guild.id] = {msg.author.id: {"count": 0, "content": msg.content}}
            if not msg.author.id in msgs[msg.guild.id]:
                msgs[msg.guild.id][msg.author.id] = {"count": 0, "content": msg.content}
            if spamer(msg, "antiflood"):
                try: v = cache.antiflood_data[msg.guild.id]
                except: v = {}
                try:
                    max1 = v['max']
                except:
                    max1 = 3
                if msgs[msg.guild.id][msg.author.id]["count"] < max1:
                    if msgs[msg.guild.id][msg.author.id]["content"] == msg.content:
                        msgs[msg.guild.id][msg.author.id]["count"] += 1
                else:
                    def check(m):
                        return m.author == msg.author
                    await msg.channel.purge(limit = max1 + 1, check = check)
                    await msg.channel.send(f'{msg.author.mention}, здесь запрещено флудить.', delete_after = 10.0)
                    try:
                        pdict = v['punishment']
                    except:
                        pdict = {"type": "none", "duration": 0}
                    if pdict['duration'] == 0:
                        pdict['duration'] = 228133722
                    if pdict['type'] == 'mute':
                        await punishments.tempmute(msg, msg.author, pdict['duration'])
                    elif pdict['type'] == 'warn':
                        await punishments.warn(msg, msg.author)
                    elif pdict['type'] == 'kick':
                        await msg.author.kick(reason = "Анти-флуд")
                    elif pdict['type'] == 'ban':
                        if pdict['duration'] == 228133722:
                            await msg.author.ban(reason = "Анти-флуд")
                        else:
                            await msg.author.ban(reason = f"Анти-флуд | {word.hms(pdict['duration'])}")
                        await punishments.tempban(msg, msg.author, pdict['duration'])
            self.bot.loop.create_task(clear_af(msg.guild, msg.author))'''
                    
            
def setup(bot):
    bot.add_cog(AntiSpam(bot))
