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
