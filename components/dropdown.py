import discord

class Dropdown(discord.ui.Select):
    def __init__(self, bot):
        self.bot = bot
        options = [
            discord.SelectOption(label='A1', description="Tri bom!", emoji='🟩'),
            discord.SelectOption(label="A2", description="Bah, ta ficando legal", emoji='🟦'),
            discord.SelectOption(label='A3', description="Tchê, ainda da pro gasto", emoji='🟥'),
            discord.SelectOption(label="B1", description="Bah, nem da pro cheiro", emoji="🟨")
        ]

        super().__init__(placeholder="Escolhe o qualis que tu quer, guri!", min_values=1, max_values=1, options=options)
    
    async def callback(self, interaction: discord.Interaction):
        print(self.values)
        await interaction.response.send_message(f"Papers filtrados pelo qualis: {self.values[0]}")
        await self.bot.filter_by_qualis(self.values[0])

class DropdownView(discord.ui.View):
    def __init__(self, bot):
        super().__init__()
        self.add_item(Dropdown(bot))
