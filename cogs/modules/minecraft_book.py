from asyncio import gather, sleep, create_task
from asyncio.exceptions import TimeoutError
from time import time

class Book:
  def __init__(self, ctx, embeds, events=None, nav_arrows=True , update_pages=None):
    """pages being a list of embeds, msg is the message object,
     events being a list of extra reactions and subsequent events (corresponding to pages)"""
    # like pages =  [embed1, embed2] 
    # msg = discord.Message
    # events = [{emoji:(func, arg), emoji:(func, arg)}]
    # update_pages optional argument that takes function that derives your pages (embeds)
    self.ctx = ctx
    self.user_id = ctx.author.id
    self.bot = ctx.bot
    self.update_pages = update_pages or None
    self.embeds = embeds
    self.pg = 0
    self.events = events or [{}]*len(embeds)
    self.reacts = []

    # adding left right page navigation
    if nav_arrows:
      arrow_events = {"<:prevpg:780564661275852890>": (self.pgPv, None),
                      "<:nextpg:780564809296904233>": (self.pgNx, None)}
      for i in range(len(self.events)):
        self.events[i].update(arrow_events)


  # add react to a message
  async def my_react(self, msg, emoji):
    self.reacts.append(emoji) # tracking the reacts the bot applies
    await msg.add_reaction(emoji)

  # remove all of a react from a message
  async def my_unreact(self, msg, emoji):
    self.reacts.remove(emoji) # tracking the reacts the bot applies
    await msg.clear_reaction(emoji)

  async def run(self):  # cannot await in init func
    self.msg = await self.ctx.send(embed=self.embeds[self.pg])
    # when the bot is listening for reactions this has the valid reacts (per page)
    self.listen_reacts = []
    for event in self.events:
      pg_reacts = []
      for emoji in event.keys():
        pg_reacts.append(emoji)
      self.listen_reacts.append(pg_reacts)
    
    await self.listen()
  
  async def pgNx(self):
    await self.pgSet(self.pg+1)

  async def pgPv(self):
    await self.pgSet(self.pg-1)

  async def pgSet(self, num):
    if num < 0:
      self.pg = len(self.embeds) + num
    elif num >= len(self.embeds):
      self.pg = num - len(self.embeds)
    else:
      self.pg = num
    await gather(self.update_reacts(),
                         self.msg.edit(embed=self.embeds[self.pg]))

  async def add_reacts(self):
    tasks = []
    for emoji in self.events[self.pg].keys():
      if emoji not in self.reacts:
        tasks.append(self.my_react(self.msg, emoji))
    if tasks != []:
      await gather(*tasks)
    
  async def clear_unused_reacts(self):
    tasks = []
    for emoji in self.reacts:
      if emoji not in self.listen_reacts[self.pg]:
        tasks.append(self.my_unreact(self.msg, emoji))
    if tasks != []:
      await gather(*tasks)

  async def update_reacts(self):
    await gather(self.add_reacts(), self.clear_unused_reacts())

  # checks if an reaction is the wanted one for listen
  def react_is_useful(self, reaction, user):
    if (not user.bot) \
      and (reaction.message.id == self.msg.id) \
      and (user.id == self.user_id) \
      and (str(reaction.emoji) in self.listen_reacts[self.pg]):
      return True
    return False

  async def updatePages(self):
    while True:
      self.embeds = self.update_pages()
      await self.msg.edit(embed=self.embeds[self.pg])
      await sleep(2)

  # detecting reactions to change pages & do functions
  async def listen(self):
    if self.update_pages != None:
      task = create_task(self.updatePages())
    finaltime = 300+time()
    endtime = 60+time()
    while (time() < endtime) and (time() < finaltime):
      try:
        # basically runs the wait_for reaction and the add reacts together
        results = await gather(self.bot.wait_for('reaction_add', timeout=30.0, 
                                                         check=self.react_is_useful),
                                       self.update_reacts())
        reaction, user = results[0]
        usr_emji = str(reaction.emoji)
        endtime += 30       
        func = self.events[self.pg][usr_emji]
        to_call = func[0](func[1]) if func[1]!=None else func[0]()
        await gather(reaction.remove(user), to_call)

        # if self.update_pages != None:
        #   self.embeds = self.update_pages()
        #   await self.msg.edit(embed=self.embeds[self.pg])

      except TimeoutError: 
        pass
        
    if self.update_pages != None:
      task.cancel()
    await self.msg.clear_reactions()
