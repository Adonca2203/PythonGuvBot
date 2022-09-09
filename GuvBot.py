import discord
from discord import app_commands
from discord import interactions
from discord.app_commands.models import AppCommand, AppCommandPermissions
from SECRET import DEV_SERVER_ID, PROD_SERVER_ID, TOKEN
from DatabaseAPI import Database

#CHANGE DEBUG WHEN READY TO DEPLOY
debug = True

if debug:
    serverID = DEV_SERVER_ID
else:
    serverID = PROD_SERVER_ID

class aclient(discord.Client):
    def __init__(self) -> None:
        super().__init__(intents=discord.Intents.default())
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync(guild = discord.Object(id = serverID))
            self.synced = True

        print(f"We have logged in as {self.user}.")

client = aclient()
tree = app_commands.CommandTree(client)

@tree.command(name="quote", description="Call upon already created quotes", guild=discord.Object(id = serverID))
async def self(interaction:discord.Interaction, name:str = "", content:str = "", author:discord.User = None):
    db = Database.instance()
    if name != "":
        try:
            quote = db.GetQuoteBy("name", name.lower())

        except Exception as e:
            print(e)
            await interaction.response.send_message(f"Could not find a quote matching that.")
            return

        if quote != None:
            await interaction.response.send_message(f"{quote.name}\n{quote.content}")
        else:
            await interaction.response.send_message(f"Could not find a quote matching that.")

    elif content != "":
        quote_list = []
        try:
            quote = db.GetQuoteBy("content", content.lower())
            for quotes in quote:
                quote_list.append(quotes)

        except Exception as e:
            print(e)
            await interaction.response.send_message(f"Could not find a quote matching that.")
            return

        if quote != None:
            for quote in quote_list:
                await interaction.response.send_message(f"{quote.name}\n{quote.content}")

        else:
            await interaction.response.send_message(f"Could not find a quote matching that.")

    elif author != -1:
        quote_list = []
        try:
            quote = db.GetQuoteBy("uid", author.id)
            for quotes in quote:
                quote_list.append(quotes)

        except Exception as e:
            print(e)
            await interaction.response.send_message(f"Could not find a quote matching that.")
            return
        
        for quote in quote_list:
            await interaction.response.send_message(f"{quote.name}\n{quote.content}")

@tree.command(name="create-quote", description="Add a new quote", guild=discord.Object(id = serverID))
async def self(interaction:discord.Interaction, name:str, content:str):
    db = Database.instance()
    try:
        db.CreateQuote(interaction.user.id, name.lower(), content)

    except Exception as e:
        print(e)
        await interaction.response.send_message("Quote could not successfully be created.")
        return

    await interaction.response.send_message("Quote successfully created!")

@tree.command(name="remove-quote", description="Remove a quote", guild=discord.Object(id = serverID))
@app_commands.default_permissions(administrator = True)
async def self(interaction:discord.Interaction, name:str = "", content:str = "", user:discord.User = None):
    db = Database.instance()
    if name != "":
        try:
            db.RemoveQuoteBy("name", name.lower())
        except Exception as e:
            print(e)
            await interaction.response.send_message(f"Could not find a quote matching that.")
            return

        await interaction.response.send_message(f"Successfully removed the quote.")
    elif content != "":
        try:
            db.RemoveQuoteBy("content", content.lower())
        except Exception as e:
            print(e)
            await interaction.response.send_message(f"Could not find a quote matching that.")
            return

        await interaction.response.send_message(f"Successfully removed the quote.")
    elif user != None:
        try:
            db.RemoveQuoteBy("uid", user.id)
        except Exception as e:
            print(e)
            await interaction.response.send_message(f"Could not find a quote matching that.")
            return

        await interaction.response.send_message(f"Successfully removed the quote.")

client.run(TOKEN)
