"""
===

MIT License

Copyright (c) 2018 Dusty.P https://github.com/dustinpianalto

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""


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
