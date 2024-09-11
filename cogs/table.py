from discord.ext import commands, tasks
import pandas as pd
import numpy as np
from components.pagination import PaginationView
from  utils.generate_table import generate_table
from logging import log, INFO
import asyncio
from datetime import date, timedelta

class TableCog(commands.Cog):
    def __init__(self, bot: commands.Bot, table_path, keys_path, warning_channel=734886532090953746, deadline_threshold=10):
        self.bot                = bot
        self.table_path         = table_path
        self.keys_path          = keys_path
        self.table              = None
        self.keyswords          = None
        self.date               = None
        self.warning_channel    = warning_channel
        self.deadline_threshold = deadline_threshold
        self.__read_table()
        self.__refresh_table.start()
        self.__warning.start()
    
    def cog_unload(self):
        self.__refresh_table.cancel()
        self.__warning.cancel()

    async def on_ready(self):
        print(f"Logged in as {self.usef} (ID: {self.user.id}) - TableCog")

    @commands.command(
        name="show",
        help="Show table with the current informations."
    )
    async def show(self, ctx):
        # log(INFO, "Show table")
        pagination = PaginationView(self.table[['sail', 'location', 'deadline', 'qualis', 'similarity']])
        await pagination.send(ctx)

    @commands.command(
        name="setdt",
        help="Defines the deadline threshold. (Days)",
        brief="Example: !setdt 15"
    )
    async def setdt(self, ctx, deadline_threshold):
        if deadline_threshold:
            log(INFO, f"Deadline setted to {deadline_threshold}")
            self.deadline_threshold = int(deadline_threshold)

    @commands.command(
        name="showdt",
        help="Show the current deadline threshold."
    )
    async def showdt(self, ctx):
        await ctx.send(f"Deadline threshold: {self.deadline_threshold} days")
    @commands.command(
        name="keys",
        help="Show keywords list."
    )
    async def keys(self, ctx):
        # log(INFO, "Show keywords")
        self.__read_keywords()
        await ctx.send(self.keyswords)

    @commands.command(
        name="rmk",
        help="Remove keywords from list.",
        brief="Example: ?rmk key_a,key_b,key_c"
    )
    async def rmk(self, ctx, str_keys = None):
        # log(INFO, "Remove key")
        if not str_keys:
            await ctx.send("It's necessary pass key words like: **!remove_keywords key_a,key_b,key_c**")
            return
        # Get current keys
        self.__read_keywords()
        self.__rmk(str_keys)
        # self.__update_table()
        await ctx.send(f"Update keywords list to: {self.keyswords}")
        # await self.show(ctx)

    @commands.command(
        name="addk",
        help="Add new keywords to keywords list.",
        brief="Example: ?addk key_a,key_b,key_c"
    )
    async def addk(self, ctx, str_keys = None):
        # log(INFO, "Add new key")
        if not str_keys:
            await ctx.send("It's necessary pass key words like: **!add_keywords key_a,key_b,key_c**")
            return

        self.__addk(key_list = str_keys)
        # self.__update_table()
        await ctx.send(f"Update keywords list to: {self.keyswords}")

    @tasks.loop(hours=24)
    async def __refresh_table(self):
        log(INFO, "Refresh table")
        self.__update_table()

    @tasks.loop(hours=(24*7))
    async def __warning(self):
        last_events = self.table[['sail', 'location', 'deadline', 'qualis', 'similarity']].loc[self.table['deadline'] <= self.date+timedelta(days=self.deadline_threshold)]
        if last_events.shape[0] > 0:
            try:
                log(INFO, f"Warning Message send to {self.warning_channel}")
                channel = self.bot.get_channel(self.warning_channel)
                await channel.send(f"# 🚨🚨 WARNING UPCOMING DEADLINE 🚨🚨")
                pagination = PaginationView(last_events)
                await pagination.send(channel)
            except:
                print("deu ruim")
                # log(INFO, f"CHANNEL id={self.warning_channel} NOT FOUND!!")
            return
        log(INFO, f"NO UPCOMING DEADLINE")
        print("NO UPCOMING DEADLINE")

    def __addk(self, key_list: str):
        # log(INFO, "Add new keywords on file")
        # Get current keys
        self.__read_keywords()
        keys = key_list.split(',')

        self.keyswords = self.keyswords + keys
        self.__savek()

    @commands.command()
    async def update(self, ctx):
        await ctx.send("# 🔄 Updating table keys... 🔄")
        self.__update_table()
        await ctx.send("# ‼️ Table updated ‼️")

    def __read_table(self):
        # log(INFO, "Read table")
        self.date = pd.to_datetime(date.today())
        self.keyswords = self.__read_keywords()
        self.table = pd.read_csv(self.table_path)
        self.table['deadline'] = pd.to_datetime(self.table['deadline'], errors='coerce')
        self.table = self.table.loc[self.table['deadline'] >= self.date]

    def __read_keywords(self):
        # log(INFO, "Read keywords")
        keys = []
        with open(self.keys_path) as f:
            keys = f.read().split('\n')
        self.keyswords = keys

    def __rmk(self, key_list: str):
        # log(INFO, f"Remove {key_list} from keys")
        keys = key_list.split(',')
        for key in keys:
            if key in self.keyswords:
                self.keyswords.pop(self.keyswords.index(key))
        self.__savek()

    def __savek(self):
        # log(INFO, "Generating new keywords file")
        with open('keywords.txt', 'w') as f:
            f.write('\n'.join(self.keyswords))

    def __update_table(self):
        generate_table()
        self.__read_table()