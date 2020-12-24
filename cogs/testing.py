from discord.ext import tasks, commands
from discord.utils import get
from discord import Embed
from random import shuffle
from time import time 
from pickle import load, dump
import datetime

#  BLANK UNICODE CHARACTER THAT CAN BE USED IN EMBEDS -->‏‏‎ ‎<--

class TestingCommands(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    class Charaters:
      hr = "\u200A" # hairline space
      thn = "\u2009" # thin space
      dirt = "<:dirt:662891513801605121>" # dirt emoji
      nums = "\u2088\u2088\u2086"
      drnm = "\u200A"+dirt+nums+"\u2005"

    self.chars = Charaters()

  @commands.command()
  async def em(self, ctx):
    c = self.chars
    embd = Embed(title="WayfaringBloke")
    embd.add_field(name="`┌──────┬`", value=f"""
      `|`{c.drnm}`|`
    """, inline = True)
    for i in range(7):
      embd.add_field(name="`──────┬`", value=f"""
      {c.drnm}`|`
    """, inline = True)
    embd.add_field(name="`──────┐`", value=f"""
      {c.drnm}`|`
    """, inline = True)
    await ctx.send(embed=embd)

  """
    ┌───┬───┬───┬───┬───┬───┬───┬───┬───┐
    {c.hr}│{c.drnm}│{c.drnm}{c.hr}│{c.drnm}│{c.drnm}│{c.drnm}{c.hr}│{c.drnm}│{c.drnm}│{c.drnm}{c.hr}│{c.drnm}│
    ├───┼───┼───┼───┼───┼───┼───┼───┼───┤
    {c.hr}│{c.drnm}│{c.drnm}{c.hr}│{c.drnm}│{c.drnm}│{c.drnm}{c.hr}│{c.drnm}│{c.drnm}│{c.drnm}{c.hr}│{c.drnm}│
    ├───┼───┼───┼───┼───┼───┼───┼───┼───┤
    {c.hr}│{c.drnm}│{c.drnm}{c.hr}│{c.drnm}│{c.drnm}│{c.drnm}{c.hr}│{c.drnm}│{c.drnm}│{c.drnm}{c.hr}│{c.drnm}│
    └───┴───┴───┴───┴───┴───┴───┴───┴───┘
    """

"""
`┌──────┬──────┬──────┬──────┬──────┬──────┬───────┬──────┬──────┐`
`|`{c.drnm}`|`{c.drnm}`|`{c.drnm}`|`{c.drnm}`|`{c.drnm}`|`{c.drnm}`|`{c.drnm}`|`{c.drnm}`|`{c.drnm}`|`
"""
def setup(bot):
  tests = TestingCommands(bot)
  bot.add_cog(tests)