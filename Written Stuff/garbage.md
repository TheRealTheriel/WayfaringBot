# Stuff we keep for no reason
WB's defunct inv class
```python
class Inventory:
  subscripts = {}
  def __init__(self, ctx, player, to_emoji):
    self.ctx = ctx
    self.player = player
    self.inv = player.inventory
    self.to_emoji = to_emoji

  def inv_string(self):
    subscript = {0:"\u2080", 1:"\u2080", 2:"\u2082", 3:"\u2083", 4:"\u2084",
                 5:"\u2085", 6:"\u2086", 7:"\u2087", 8:"\u2088", 9:"\u2089"}
    

  def gen_embed(self):
    self.embed = Embed(title=f"{self.ctx.author.name}'s Inventory <:bundle:780992430257340420>", 
                       color=0x00ff00)
    for item, amount in self.inv.items():
      self.embed.add_field(
        name=f"{self.to_emoji(item)}  *  {amount}",
        value="\~\~\~\~\~\~\~\~\~", inline=False)
    return self.embed

  async def run(self): 
    self.msg = await self.ctx.send(embed=self.gen_embed())
    while True:
      old_embed = self.embed
      self.gen_embed()
      if old_embed != self.embed:
        await self.msg.edit(embed=self.embed)
      await asyncio.sleep(2)
```