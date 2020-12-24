from discord.ext import tasks, commands
from discord.utils import get
from random import shuffle
from random import randint as bruh
from time import time 
from pickle import load, dump
from discord import Embed
import datetime

class GeneralCommands(commands.Cog):
  def __init__(self, bot):
	  self.bot = bot
	  self.split_channels = []
	  self.clip_ids = load(open("data/clips", "rb"))
	  self.author_id = 354253195129651211
	  self.uptime_  = datetime.datetime.now()

  @commands.command()
  async def test(self, ctx):
    await ctx.send(f"I am online :-) <:god:781003196876455967>")

  @commands.command()
  async def upTime(self, ctx):
    d = self.uptime_.strftime("%A %B %d, %Y")
    await ctx.send(f"WayfaringBot up since `{d}`")

  @commands.command()
  async def clip(self, ctx):
    self.clip_ids.append([ctx.channel.id, ctx.message.id, int(time()+604800)])
    await ctx.message.add_reaction('🎞️')
    dump(self.clip_ids, open("data/clips", "wb+"))

  @tasks.loop(seconds=1800)
  async def clip_vote_update(self):
    for clip in self.clip_ids:
      if clip[2] > time():
        try:
          chnnl = await self.bot.fetch_channel(clip[0])
          msg = await chnnl.fetch_message(clip[1])
          reacts = msg.reactions
        except:
          self.clip_ids.remove(clip)
          dump(self.clip_ids, open("data/clips", "wb+"))
        else:
          votes = get(reacts, emoji='🎞️').count
          if votes >= 5:
          	await msg.pin(reason="Clip")
          	self.clip_ids.remove(clip)
          	dump(self.clip_ids, open("data/clips", "wb+"))
      else:
        self.clip_ids.remove(clip)
        dump(self.clip_ids, open("data/clips", "wb+"))
  
  @commands.command()
  @commands.cooldown(rate=1, per=60)
  @commands.guild_only()
  async def split(self, ctx):
    if ctx.author.voice == None:
      await ctx.send("`ERROR:` You must be in a VC to use this command")
    else:
      chnnl = ctx.author.voice.channel
      split_ch = await chnnl.clone(name=(chnnl.name + " split"), reason="Split")
      self.split_channels.append(split_ch)
      mbrs = chnnl.members
      for mbr in mbrs:
        if mbr.bot is True:
          mbrs.remove(mbr)
      shuffle(mbrs)
      to_move = mbrs[:int(len(mbrs)/2)]
      for mbr in to_move:
        await mbr.move_to(split_ch, reason="Split")
      await ctx.send(f"`SUCCESS:` Split {', '.join(mbr.name for mbr in to_move)}")

 
  @tasks.loop(seconds=5)
  async def cullSplits(self):
    for channel in self.split_channels:
      if len(channel.members) < 2:
        await channel.delete(reason="Split")
        self.split_channels.remove(channel)

  @cullSplits.after_loop
  async def after_cullSplits(self):
    for channel in self.split_channels:
      await channel.delete(reason="Split")
    self.split_channels = []

  @commands.command(breif="sends the boys to horny jail")
  async def horny(self, ctx):
    # users must have joined a channel before the self.bot has been run for this command to work
    if 779099365352407051 not in [role.id for role in ctx.author.roles]:
        await ctx.send("`ERROR:` Not horny enough")
    else:
      voice_users = []
      for channel in ctx.guild.voice_channels:
        voice_users += channel.members
        if channel.id == 776917169395990559:
          hornyjail = channel
      if voice_users == []:
        await ctx.send("`ERROR:` No one is horny :(")
      else:
        for user in voice_users:
          await user.move_to(hornyjail, reason="you horny")
        await ctx.send("https://cdn.discordapp.com/attachments/764607000495259679/779122876943040522/f_pyFvb0461o2TB4fwhPzQxPOFfqKCOax3Vx29G1kew.jpg")

  @commands.command()
  async def jay(self, ctx):
    await ctx.send("<:jay:780571254355656746>")

  @commands.command(brief="All hail the phantom forces endgame quotes", usage="| write $quote")
  async def quote(self, ctx):
    rand_quote = bruh(0, 71)
    with open("data/quotes.txt", "r") as f:
      q = f.readlines()[rand_quote]
      q = q[:-2]  # getting rid of space and comma 
    quote_emb = Embed(title=q, color=0xff00ff)
    await ctx.send(embed=quote_emb)

def setup(bot):
  general = GeneralCommands(bot)
  #general.name = "General Commands"
  general.cullSplits.start()
  general.clip_vote_update.start()
  bot.add_cog(general)

