<p align="center">
  <img src="botche.png" width="200"><br>
  <strong>Botchê</strong>
</p>

This repository contains the source code for a Discord bot designed to manage and interact with tables of conference deadlines and related data, leveraging the Discord API through the `discord.ext` library. The bot is structured into two main components: `TableCog` and `Botche`, each encapsulated as a cog for modular management.

### Features

- **Dynamic Table Updates**: Automated updates and maintenance of tables containing deadlines and conference data.
- **Interactive Commands**: Users can view deadlines, update thresholds, and manipulate keyword lists through specific commands.
- **Automatic Warnings**: Sends warnings for upcoming deadlines based on predefined thresholds.
- **Keyword Management**: Ability to add or remove keywords that filter or modify table entries.

## Requirements

- Python 3.8+
- discord.py
- pandas
- numpy

Ensure all dependencies are installed using pip:

```bash
pip install discord.py pandas numpy
```

## Configuration
1) Set the Discord bot token in an environment variable BOTCHE_TOKEN.
2) Adjust paths and command triggers in config.json.
3) Ensure data paths for tables and keyword lists point to valid files.
```python
python bot.py
```

Ensure bot.py is the main entry script containing your main function.

## Usage
### Commands

- **?show**: Display the current table of conferences.
- **?setdt [number]**: Set the number of days for the deadline alert threshold.
- **?showdt**: Show the current deadline threshold.
- **?keys**: Display the list of active keywords.
- **?addk [keywords]**: Add keywords to the list.
- **?rmk [keywords]**: Remove keywords from the list.
- **?update**: Force an update of the data table.

## TODO
- Similarity filter
- add keywords
- Keyword filter
- Table indexing
- More command (index)
- Update table
- Warning for similarity > 10
- Add A4 to filter
