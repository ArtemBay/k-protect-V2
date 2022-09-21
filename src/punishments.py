from time import time

import disnake as discord
from disnake import Embed

from src.utils import cache
import src.word as word
from config import Color
from src.profilactic import measures


def ndm(ctx):
    try:
        curopt = cache.configs_data[ctx.guild.id]["notify-dm"]
    except KeyError:
        curopt = False
    return curopt


async def tempban(ctx, user, tc, reason="Не указана", ignore_ndm=False):
    if ndm(ctx) and not ignore_ndm:
        embed: Embed = discord.Embed(title=f"🔨 | Вы были забанены на сервере **{ctx.guild.name}**", color=Color.danger)
        embed.description = f"""
**Причина:** {reason}"""
        if tc != 228133722:
            embed.description += f"""
            **Длительность:** {word.hms(tc)}
            **Дата разбана:** <t:{int(time()) + tc}>"""
        embed.set_thumbnail(url=ctx.guild.icon_url)
        try:
            await user.send(embed=embed)
        except (Exception, BaseException):
            pass
    cache.bans.add(ctx.guild.id, {str(user.id): int(time()) + tc})


async def tempmute(ctx, user, tc, reason="Не указана", ignore_ndm=False):
    try:
        role = ctx.guild.get_role(cache.configs_data[ctx.guild.id]['muterole'])
    except (Exception, BaseException):
        role = await ctx.guild.create_role(name="KP-MUTED", permissions=discord.Permissions.none(),
                                           colour=discord.Colour(0x00ff56))
        cache.configs.add(ctx.guild.id, {"muterole": role.id})
    cache.mutes.add(ctx.guild.id, {str(user.id): int(time()) + tc})
    await user.add_roles(role)
    if ndm(ctx):
        if not ignore_ndm:
            embed = discord.Embed(color=Color.warning)
            embed.title = f"🔇 | Вы были замьючены на сервере **{ctx.guild.name}**"
            embed.description = f"""
    **Причина:** {reason}"""
            if tc != 228133722:
                embed.description += f"""
                **Длительность:** {word.hms(tc)}
                **Дата размьюта:** <t:{int(time()) + tc}>"""
            embed.set_thumbnail(url=ctx.guild.icon_url)
            try:
                await user.send(embed=embed)
            except (Exception, BaseException):
                pass
    for channel in ctx.guild.text_channels:
        await channel.set_permissions(role, send_messages=False, add_reactions=False)
    for channel in ctx.guild.voice_channels:
        await channel.set_permissions(role, speak=False)


async def unmute(ctx, user):
    measures.add(what=7)
    if ctx.guild.id in cache.configs_data:
        cache.mutes.delete(ctx.guild.id, {str(user.id): True})
        if "muterole" in cache.configs_data[ctx.guild.id]:
            role = ctx.guild.get_role(cache.configs_data[ctx.guild.id]['muterole'])
            if role is not None:
                await user.remove_roles(role)


async def lockbot(ctx, user, tc):
    measures.add(what=7)
    managed_role = [r for r in user.roles if r.managed][0]
    other_roles = [r.id for r in user.roles if not r.managed]
    cache.locks.add(ctx.guild.id, {str(user.id): {"locked": int(time()) + tc, "roles": other_roles,
                                                  "managed": {"id": managed_role.id,
                                                              "perms": managed_role.permissions.value}}})
    for role in [r for r in user.roles if not r.managed]:
        try:
            await user.remove_roles(role)
        except (Exception, BaseException):
            pass
    await managed_role.edit(permissions=discord.Permissions.none())


async def unlockbot(ctx, user):
    measures.add(what=7)
    managed_role = [r for r in user.roles if r.managed][0]
    if ctx.guild.id in cache.locks_data:
        managed_perms_value = cache.locks_data[ctx.guild.id][str(user.id)]['managed']['perms']
        managed_perms = discord.Permissions(permissions=managed_perms_value)
        role_ids = cache.locks_data[ctx.guild.id][str(user.id)]['roles']
        for role in role_ids:
            try:
                r = ctx.guild.get_role(role)
                await user.add_roles(r)
            except (Exception, BaseException):
                pass
        await managed_role.edit(permissions=managed_perms)
        cache.locks.delete(ctx.guild.id, {str(user.id): True})


async def checkwarns(ctx, user):
    measures.add(what=7)
    if ctx.guild.id in cache.warns_data:
        warns = cache.warns_data[ctx.guild.id]
        uwarns = warns['members'][str(user.id)]
        if 'actions' in warns:
            actions = warns['actions']
            if str(uwarns) in actions:
                # if actions[str(uwarns)]['duration'] == 0:
                #     duration = 228133722
                # else:
                #     duration = actions[str(uwarns)]['duration']
                ptype = duration = actions[str(uwarns)]['punishment']
                embed = discord.Embed()
                if ptype == 'mute':
                    await tempmute(ctx, user, duration)
                    embed.colour = Color.success
                    if duration == 228133722:
                        embed.title = '🔇 | Мьют'
                        embed.description = f'''
**Пользователь:** {user} ({user.mention})
**Модератор:** K-Protect#0952 (<@356737308898099201>)
**Причина:** Накоплено **{uwarns}** {word.word_correct(uwarns, 'предупреждение', "предупреждения", "предупреждений")}
                        '''
                    else:
                        embed.title = '🔇 | Временный мьют'
                        embed.description = f'''
**Пользователь:** {user} ({user.mention})
**Модератор:** K-Protect#0952 (<@356737308898099201>)
**Время:** {word.hms(float(duration))}
**Причина:** Накоплено **{uwarns}** {word.word_correct(uwarns, 'предупреждение', "предупреждения", "предупреждений")}
                        '''
                    await ctx.send(embed=embed)
                elif ptype == 'ban':
                    await tempban(ctx, user, duration)
                    embed.colour = Color.danger
                    if duration == 228133722:
                        embed.title = '🔨 | Бан'
                        embed.description = f'''
**Пользователь:** {user} ({user.mention})
**Модератор:** K-Protect#0952 (<@356737308898099201>)
**Причина:** Накоплено **{uwarns}** {word.word_correct(uwarns, 'предупреждение', "предупреждения", "предупреждений")}
                        '''
                        await user.ban(
                            reason=f"Накоплено **{uwarns}** "
                                   f"{word.word_correct(uwarns, 'предупреждение', 'предупреждения', 'предупреждений')}")
                    else:
                        embed.title = '🔨 | Временный бан'
                        embed.description = f'''
**Пользователь:** {user} ({user.mention})
**Модератор:** K-Protect#0952 (<@356737308898099201>)
**Время:** {word.hms(float(duration))}
**Причина:** Накоплено **{uwarns}** {word.word_correct(uwarns, 'предупреждение', "предупреждения", "предупреждений")}
                        '''
                    await user.ban(
                        reason=f"Накоплено **{uwarns}** "
                               f"{word.word_correct(uwarns, 'предупреждение', 'предупреждения', 'предупреждений')} | "
                               f"{word.hms(float(duration))}")
                    await ctx.send(embed=embed)
                elif ptype == 'kick':
                    await user.kick(
                        reason=f"Накоплено **{uwarns}** "
                               f"{word.word_correct(uwarns, 'предупреждение', 'предупреждения', 'предупреждений')}")
                    embed.title = '👢 | Кик'
                    embed.colour = Color.success
                    embed.description = f'''
**Пользователь:** {user} ({user.mention})
**Модератор:** K-Protect#0952 (<@356737308898099201>)
**Причина:** Накоплено **{uwarns}** {word.word_correct(uwarns, 'предупреждение', "предупреждения", "предупреждений")}
                    '''
                    await ctx.send(embed=embed)


async def warn(ctx, user, amount=1, reason="Не указана", ignore_ndm=False):
    measures.add(what=7)
    if ctx.guild.id not in cache.warns_data:
        cache.warns.add(ctx.guild.id, {'case': 1, 'members': {}, 'actions': {}})
    try:
        warns = cache.warns_data[ctx.guild.id]
    except (Exception, BaseException):
        warns = {'case': 1, 'members': {}, 'actions': {}}
    if not str(user.id) in warns['members']:
        warns['members'][str(user.id)] = amount
    else:
        warns['members'][str(user.id)] += amount
    warns['case'] += 1
    cache.warns.add(ctx.guild.id, warns)
    if ndm(ctx):
        if not ignore_ndm:
            embed = discord.Embed(color=Color.warning)
            embed.title = f"⚠ | Вы получили предупреждение на сервере **{ctx.guild.name}**"
            embed.description = f"""
    **Причина:** {reason}"""
            embed.set_thumbnail(url=ctx.guild.icon_url)
            try:
                await user.send(embed=embed)
            except (Exception, BaseException):
                pass
    await checkwarns(ctx, user)
    return warns['case'], warns['members'][str(user.id)]


async def unwarn(ctx, user, amount=1):
    measures.add(what=7)
    if ctx.guild.id in cache.warns_data:
        warns = cache.warns_data[ctx.guild.id]
        if str(user.id) in warns['members']:
            if warns['members'][str(user.id)] < amount:
                amount = warns['members'][str(user.id)]
            warns['members'][str(user.id)] -= amount
            cache.warns.add(ctx.guild.id, warns)
            return amount
        else:
            return False
    else:
        return False


async def add_qua(guild, author, user, tc, reason):
    try:
        role = guild.get_role(cache.quarantine_data[guild.id]['role'])
    except (Exception, BaseException):
        role = None

    if tc == 0:
        tc = 228133722

    if guild.get_member(user.id):
        user = guild.get_member(user.id)
        for r in user.roles:
            try:
                await user.remove_roles(r)
            except (Exception, BaseException):
                pass
        if user.bot:
            await lockbot(user, user, tc)
        if role:
            await user.add_roles(role)

    dictionary = {
        "begin": int(time()),
        "orderly": author.id,
        "end": int(time()) + tc,
        "reason": reason
    }

    cache.quarantine.add(guild.id, {str(user.id): dictionary})


async def rem_qua(guild, _id):
    cache.quarantine.delete(guild.id, {str(_id): True})
    try:
        role = guild.get_role(cache.quarantine_data[guild.id]['role'])
    except (Exception, BaseException):
        role = None
    if guild.get_member(_id) and role:
        await guild.get_member(_id).remove_roles(role)
    if guild.get_member(_id).bot:
        await unlockbot(guild.get_member(_id), guild.get_member(_id))
