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
import logging

events_log = logging.getLogger('events')


class BotEvents:
    def __init__(self, bot):
        self.bot = bot

    async def on_guild_join(self, guild):
        await self.bot.db_con.execute("insert into guild_config(guild_id, channel_lockdown, admin_roles) "
                                      "values ($1, $2, $3)", guild.id, False, [guild.role_hierarchy[0].id])
        events_log.info(f'Entry Created for {guild.name}')
        await guild.me.edit(nick='[!] Submitter')

    async def on_guild_remove(self, guild):
        await self.bot.db_con.execute(f'delete from guild_config where guild_id = $1', guild.id)
        events_log.info(f'Left the {guild.name} guild.')


def setup(bot):
    bot.add_cog(BotEvents(bot))
