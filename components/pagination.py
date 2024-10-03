import discord
import pandas as pd
from table2ascii import table2ascii as t2a, PresetStyle

class PaginationView(discord.ui.View):
    current_page: int = 1
    sep: int = 5
    total_pages: int = None
    options = [
        discord.SelectOption(label='ALL', description="Ta louco! Qualquer um ta servindo, tchê", emoji='🟩'),
        discord.SelectOption(label='A1', description="Tri bom!", emoji='🟩'),
        discord.SelectOption(label="A2", description="Bah, ta ficando legal", emoji='🟦'),
        discord.SelectOption(label='A3', description="Tchê, ainda da pro gasto", emoji='🟥'),
        discord.SelectOption(label="B1", description="Bah, nem da pro cheiro", emoji="🟨")
    ]
    def __init__(self, data: pd.DataFrame):
        self.table = data
        self.filtered_table = data.copy()
        self.total_pages = self.calculate_total_page()
        super().__init__()

    def calculate_total_page(self):
        return int(self.filtered_table.shape[0] / self.sep) + 1

    async def send(self, ctx):
        self.message = await ctx.send(view=self)
        await self.update_message(self.filtered_table[0:5])

    def create_message(self, data):
        data['deadline'] = data['deadline'].astype(str)

        data = data.rename(columns={k: k.upper() for k in data.columns})
        data.reset_index(inplace=True)
        data.rename(columns={'index': 'ID'}, inplace=True)
        ascii_table = t2a(
            header=data.columns.tolist(),
            body=data.values.tolist(),
            style=PresetStyle.double_thin_compact
        )
        
        return f"""
        ## 📅 Conference Table
        ### 📄 Total Pages: {self.total_pages} \t\t|\t\t 📄 Current Page: {self.current_page}
        ```{ascii_table}```
        \n\* significa que provavelmente o qualis não está correto! 🚩
        \n?more id Para coletar mais informações sobre a conferência 🚩
        """

    def update_table_info(self):
        self.total_pages = self.calculate_total_page()

    async def update_message(self, data):
        self.update_buttons()
        await self.message.edit(content=self.create_message(data), view=self)

    def update_buttons(self):
        print(f"Current Page: {self.current_page}")
        
        self.children[0].disabled = self.current_page == 1
        self.children[1].disabled = self.current_page == self.total_pages

    def filter_by_qualis(self, qualis):
        if qualis == "ALL":
            self.filtered_table = self.table.copy()
            return
        self.filtered_table = self.table.loc[self.table['qualis'] == qualis]

    @discord.ui.button(label='<', style=discord.ButtonStyle.primary)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page -= 1
        until_item = self.current_page * self.sep
        from_item = until_item - self.sep
        await self.update_message(self.filtered_table[from_item:until_item])

    @discord.ui.button(label='>', style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page += 1
        until_item = self.current_page * self.sep
        from_item = until_item - self.sep
        await self.update_message(self.filtered_table[from_item:until_item])

    @discord.ui.select(placeholder="Escolhe o qualis que tu quer, guri!", min_values=1, max_values=1, options=options)
    async def filter(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        print(f"FILTRANDO por {interaction.data['values']}...")
        self.filter_by_qualis(interaction.data['values'][0])
        self.update_table_info()
        print("ATUALIZANDO")
        await self.update_message(self.filtered_table)
