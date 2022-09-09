import discord
from discord import app_commands
from discord.embeds import Embed
from SECRET import DEV_SERVER_ID, PROD_SERVER_ID, TOKEN, EMOTE_CALLING_CARD
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

async def BuildMessage(name:str, content:str) -> discord.Embed:
    embed = discord.Embed(title=name.capitalize(), description=content.capitalize()+" "+EMOTE_CALLING_CARD, color=0xC0C738)
    return embed

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

        if quote:
            message = await BuildMessage(quote.name, quote.content)
            await interaction.response.send_message(embed=message)
        else:
            await interaction.response.send_message(f"Could not find a quote matching that.")

    elif content != "":
        quote_list = []
        try:
            quote = db.GetQuoteBy("content", content.lower())
            if quote:
                for quotes in quote:
                    quote_list.append(quotes)

            else:
                await interaction.response.send_message("Quote successfully created!")

        except Exception as e:
            print(e)
            await interaction.response.send_message(f"Could not find a quote matching that.")
            return

        if quote:
            for quoteVal in quote_list:
                message = await BuildMessage(quoteVal.name, quoteVal.content)
                await interaction.response.send_message(embed=message)

        else:
            await interaction.response.send_message(f"Could not find a quote matching that.")

    elif author != -1:
        quote_list = []
        try:
            quote = db.GetQuoteBy("uid", author.id)
            if quote:
                for quotes in quote:
                    quote_list.append(quotes)

            else:
                await interaction.response.send_message("Could not find a quote matching that.")
        except Exception as e:
            print(e)
            await interaction.response.send_message(f"Could not find a quote matching that.")
            return
        
        if quote:
            for quoteVal in quote_list:
                message = await BuildMessage(quoteVal.name, quoteVal.content)
                await interaction.response.send_message(embed=message)

@tree.command(name="create-quote", description="Add a new quote", guild=discord.Object(id = serverID))
async def self(interaction:discord.Interaction, name:str, content:str):
    db = Database.instance()
    try:
        created = db.CreateQuote(interaction.user.id, name.lower(), content)

        if created:
            await interaction.response.send_message("Quote successfully created!")
        else:
            await interaction.response.send_message("Could not create that quote, it may already exists or you may be blacklisted.")

    except Exception as e:
        print(e)
        await interaction.response.send_message("Quote could not successfully be created.")
        return

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

@tree.command(name="blacklist-user", description="Blacklist an user from using me.", guild=discord.Object(id = serverID))
@app_commands.default_permissions(administrator = True)
async def self(interaction:discord.Interaction, user:discord.User):
    db = Database.instance()
    try:
        db.AddBlacklist(user.id, interaction.user.id)

    except Exception as e:
        print(e)
        await interaction.response.send_message(f"Could not blacklist that user.")
        return

    await interaction.response.send_message(f"Blacklisted the user.")

@tree.command(name="unblacklist-user", description="Remove a blacklisted user.", guild=discord.Object(id = serverID))
@app_commands.default_permissions(administrator = True)
async def self(interaction:discord.Interaction, user:discord.User):
    db = Database.instance()
    try:
        db.RemoveBlacklist(user.id)
    except Exception as e:
        print(e)
        await interaction.response.send_message(f"Could not unblacklist that user.")
        return

    await interaction.response.send_message(f"Unblacklisted the user.")

client.run(TOKEN)
