import os
import discord
from keep_alive import keep_alive
from discord.ext import commands
from discord_slash import SlashCommand
from discord_slash import SlashContext

bot = commands.Bot(
    command_prefix="$",  
    case_insensitive=True,
    intents=discord.Intents.all(), # only for slash commands
)

@bot.event
async def on_ready():
    print("Wayfaringbot online")

extensions = [
    'cogs.general',
    'cogs.minecraft',
    'cogs.testing',
]

if __name__ == '__main__':  
	for extension in extensions:
		bot.load_extension(extension)  


slash = SlashCommand(bot)
@slash.slash(name="test")
async def _test(ctx: SlashContext):
    await ctx.send(content="test", embeds=[embed])


keep_alive()  # Starts a webserver to be pinged.
token = os.environ.get("DISCORD_BOT_SECRET")
bot.run(token)  # Starts the bot
