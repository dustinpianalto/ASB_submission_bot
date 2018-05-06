import discord

owner_id = 351794468870946827


async def is_admin(bot, ctx):
    admin_roles = await bot.db_con.fetchval("select admin_roles from guild_config where guild_id = $1", ctx.guild.id)
    for role in admin_roles:
        if discord.utils.get(ctx.guild.roles, id=admin_roles[role]) in ctx.message.author.roles:
            return True
    return ctx.message.author.id == ctx.guild.owner.id or ctx.message.author.id == owner_id


def is_guild_owner(ctx):
    if ctx.guild:
        return ctx.message.author.id == ctx.guild.owner.id or ctx.message.author.id == owner_id
    return False
