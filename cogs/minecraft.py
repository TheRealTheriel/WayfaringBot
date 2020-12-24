from discord.ext import tasks, commands
from discord.utils import get
from discord import Embed
from discord import Member
from pickle import load, dump
from .modules.minecraft_book import Book
from time import time
import random
import asyncio

class Subscript:
  
  subMap = {"0":"\u2080", "1":"\u2080", "2":"\u2082", "3":"\u2083", "4":"\u2084",
            "5":"\u2085", "6":"\u2086", "7":"\u2087", "8":"\u2088", "9":"\u2089"}

  @staticmethod
  def toSubscript(num):  # takes int, returns a string of the equivilant subscript
    digits = list(str(num))
    sub = ""
    for digit in digits:
      sub += Subscript.subMap[digit]
    return sub



class EnchantedBook:  # idk why this is a class maybe it will be good later on
  def __init__(self, enchant):
    self.enchant = enchant


class Tool:
  def __init__(self, name, durability, level, enchants=None):
    
    # the default tool will be hand, which has infinite uses, a mining level of 0, and no enchants: Tool("hand", 0, 0)
    self.name = name  # name of the tool. ex iron pickaxe
    self.durability = durability  # durability of the tool
    self.level = level  # the level at which certain blocks can be mined
    self.enchants = [] if enchants is None else enchants # should be a list
    self.maxDurability = durability  # the max durability of the tool

  @staticmethod
  def getToolDurability(name):
    durabilities = {
      "wooden_pickaxe": 59,
      "stone_pickaxe": 131,
      "iron_pickaxe": 250,
      "diamond_pickaxe": 1561
    }
    return durabilities[name]

  @staticmethod
  def getToolLevel(name):
    durabilities = {
      "wooden_pickaxe": 1,
      "stone_pickaxe": 2,
      "iron_pickaxe": 3,
      "diamond_pickaxe": 4
    }
    return durabilities[name]

  def getEnchants(self):
    return [book.enchant for book in self.enchants]

  def isBroken(self):
    # checks if the tool is broken and that the tool is not the players hand
    return self.durability-1 > 0 if self.level != 0 else True

  def decreaseDur(self): # decreases the durability of the pickaxe
    
    # will check if player has an unbreaking book on their pickaxe, and if they do there is a chance their durability will not change also yw for doing it in one line jay ik u like dat
    self.durability -= 1 if "unbreaking_book" not in self.getEnchants() else random.choice([0,1,1])


class Player:
  def __init__(self, ID):
    self.ID = ID  # discord id
    self.inventory = {}
    self.mine_timer = time()
    self.tools = []
    self.inHand = Tool("hand", 0, 0)

  def getLootTables(self, table):
    # table: {block: chance}
    loot_table = []
    for block, chance in table.items():
      for i in range(chance):
        loot_table.append(block)
    return loot_table

  def mine(self): # returns a block that the player has mined

    if not self.inHand.isBroken():  # if the tool is broken
      print(f"Tool broken {self.inHand.durability}")
      return None

    if self.inHand.level == 0:  # hand
      # mineables = mineables[:2]
      drop_chances = {
        "oak_log": 1,
        "dirt": 1
      }
      block = random.choice(self.getLootTables(drop_chances))

    elif self.inHand.level == 1:  # wooden_pickaxe
      drop_chances = {
        "oak_log": 1,
        "dirt": 2,
        "cobblestone": 3
      }
      block = random.choice(self.getLootTables(drop_chances))

    elif self.inHand.level == 2:  # stone_pickaxe
      drop_chances = {
        "dirt": 5,
        "cobblestone": 9,
        "iron_ingot": 1
      }
      block = random.choice(self.getLootTables(drop_chances))

    elif self.inHand.level == 3:  # iron_pickaxe
      drop_chances = {
        "cobblestone": 31,
        "iron_ingot": 9,
        "gold_ingot": 4,
        "redstone_dust": 5,
        "diamond": 1
      }
      block = random.choice(self.getLootTables(drop_chances))

    elif self.inHand.level == 4:  # diamond_pickaxe
      drop_chances = {
        "cobblestone": 24,
        "iron_ingot": 17,
        "gold_ingot": 11,
        "redstone_dust": 12,
        "diamond": 8
      }
      block = random.choice(self.getLootTables(drop_chances))

    if self.inHand.level != 0:
      self.inHand.decreaseDur()
    return block




      



class MinecraftCommands(commands.Cog):
  def __init__(self, bot):
	  self.bot = bot

  @staticmethod
  def toEmoji(item):
    emojiRef = {  # discord emoji references
      "stone": "<:stone:662884980304773141>",
      "hand": "<:stevehand:663161843111428103>",
      "wooden_pickaxe": "<:wooden_pickaxe:665628195319578685>",
      "stone_pickaxe": "<:stone_pickaxe:665628204970541087>",
      "iron_pickaxe": "<:iron_pickaxe:665628213053227028>",
      "diamond_pickaxe": "<:diamond_pickaxe:665628223022825472>",
      "oak_log": "<:oaklog:662891560832335913>",
      "planks": "<:oakwood:662891574887448578>",
      "dirt": "<:dirt:662891513801605121>",
      "stick": "<:stick:665628184426971146>",
      "iron_ingot": "<:iron_ingot:665628230723698698>",
      "gold_ingot": "<:gold_ingot:665628239779332126>",
      "redstone_dust": "<:redstone_dust:784190446343684117>",
      "redstone_block": "<:redstone_block:784190459902951424>",
      "cobblestone": "<:cobblestone:662891817699639337>",
      "diamond": "<:diamond:665628248457084954>",
      "diamond_block": "<:diamondblock:662891483187249158>",
      "emerald": "<:emerald:670040362982572072>",
      "efficiency_book": "<a:Enchanted_Book:670100484257873932> (***Efficiency***)",
      "unbreaking_book": "<a:Enchanted_Book:670100484257873932> (***Unbreaking***)",
      "mending_book": "<a:Enchanted_Book:670100484257873932> (***Mending***)",
      "haste": "<a:haste_potion:670102526426611713>",
      "luck": "<a:luck_potion:670102526388994078>"
    }
    return emojiRef[item]

 
  def createPlayer(self, playerID):
    with open("data/minecraft/playerdata.pickle", "rb") as f:  # with statement will close the file after the contents has been run
      Data = load(f)
    Data.update({playerID: Player(playerID)})
    with open("data/minecraft/playerdata.pickle", "wb") as f:
      dump(Data, f)

  
  def isPlayer(self, playerID):  # the player id is equivilant to ctx.author.id
    with open("data/minecraft/playerdata.pickle", "rb") as f:
      Data = load(f)
    return True if playerID in Data.keys() else False

  
  def checker(self, playerID):  # should be run at the beginning of every cmd
    if (not self.isPlayer(playerID)):
      self.createPlayer(playerID)

  
  @staticmethod
  def getPlayerData(playerID):  # returns the player object of the discord user
    with open("data/minecraft/playerdata.pickle", "rb") as f:
      Data = load(f)
    player = Data[playerID]
    removeItems = []
    for item, amount in player.inventory.items():
      if amount <= 0:
        removeItems.append(item)
    for item in removeItems:
      del player.inventory[item]
    return player


  @staticmethod
  def savePlayerData(playerID, newData):  # newData should be a updated player object
    with open("data/minecraft/playerdata.pickle", "rb") as f:
      Data = load(f)
    Data.update({playerID: newData})
    with open("data/minecraft/playerdata.pickle", "wb") as f:
      dump(Data, f)

  
  @commands.command()
  async def reset(self, ctx):
    Data = {}
    with open("data/minecraft/playerdata.pickle", "wb") as f:
      dump(Data, f)
    with open("data/minecraft/playerdata.pickle", "rb") as f:
      print(load(f))
    await ctx.message.add_reaction("<:checkmate:665423250855165968>")

  
  @commands.command()
  async def mine(self, ctx):
    self.checker(ctx.author.id)  # checks if the player is in the database, if not creates a player obj for them

    player = self.getPlayerData(ctx.author.id)

    #minetimer
    if player.mine_timer > time():
      print(player.mine_timer-time())
      return
    else:
      pickaxe_constant = player.inHand.level/4  # determines speed of pickaxe type
      if "efficiency_book" in player.inHand.getEnchants():
        get_time = time() + 3 - pickaxe_constant  
      else:
        get_time = time() + 5 - pickaxe_constant
      player.mine_timer = get_time

    #creating embed
    block = player.mine()
    if block is not None:  # if block is none then pickaxe is broken
      embed=Embed(title=f"{ctx.author.name}", description=f"{self.toEmoji(player.inHand.name)}  *mining...*", color=0x00ff00)
      msg = await ctx.send(embed=embed)
    else:
      embed=Embed(title=f"Oh no!", description=f"your {self.toEmoji(player.inHand.name)} is broken!", color=0xff0000)
      msg = await ctx.send(embed=embed)
      return
    
    #saving new players inventory
    player.inventory.update({block: player.inventory.get(block, 0) + 1})
    self.savePlayerData(ctx.author.id, player)
    # with open("data/minecraft/playerdata.pickle", "rb") as f:
    #   print(load(f)[ctx.author.id].inventory)

    #minetimer
    await asyncio.sleep(get_time-time())

    minedEmbed = Embed(title=f"{ctx.author.name}", description=f"mined {self.toEmoji(block)} using {self.toEmoji(player.inHand.name)}", color=0x00ff00)
    await asyncio.gather(msg.edit(embed=minedEmbed), msg.add_reaction("<:checkmark:665613096689336320>"))


  @commands.command(aliases=['inv'])
  async def inventory(self, ctx):  
    self.checker(ctx.author.id)
    inv = Inventory(ctx)
    await inv.run()


  @commands.command()
  async def craft(self, ctx):
    self.checker(ctx.author.id)
    player = self.getPlayerData(ctx.author.id)
    table = Crafting(ctx, player)
    await table.run()


  @commands.command(aliases=["e"])
  async def craft_inventory(self, ctx):
    await asyncio.gather(self.inventory(ctx), self.craft(ctx))


  @commands.command()
  async def gift(self, ctx, member: Member):
    other = member
    self.checker(ctx.author.id)
    self.checker(other.id)
    gift = Gift(ctx, other)
    await gift.run()


class Gift(Book):
  def __init__(self, ctx, other):
    self.ctx = ctx
    self.other = other
    self.player = MinecraftCommands.getPlayerData(ctx.author.id)
    embeds = self.genTradeEmbs(initial_call=True)
    super().__init__(ctx, embeds, nav_arrows=None)
    self.events = []
    self.genPageEvents()


  def getBasicPages(self):  # returns a 2D array with 3 item names per list
    formattedItems = []
    item_list = list(self.player.inventory.keys())
    for i in range(len(item_list)):
      if i % 3 == 0:
        formattedItems.append([])
        formattedItems[-1].append(item_list[i])
      else:
        formattedItems[-1].append(item_list[i])
    return formattedItems


  def genTradeEmbs(self, initial_call=False):
    embeds = []
    formattedItems = self.getBasicPages()
    total_pages = len(formattedItems)
    page = 1
    toSub = Subscript.toSubscript
    for items in formattedItems:
      new_Embed = Embed(title=f"Gifting a   <a:dirt_present:670105760138657843>    to {self.other.name}!", color=0x00ff00)
      new_Embed.set_footer(text=f"Page {page}/{total_pages}")
      for item in items:
        amount = self.player.inventory[item]
        new_Embed.add_field(name=f"‏‏‎ \n{MinecraftCommands.toEmoji(item)}{toSub(amount)}", value="‎‎‏‏‎ ‎")
      page += 1
      embeds.append(new_Embed)
    if initial_call:
      return embeds
    else:
      self.embeds = embeds


  def genPageEvents(self):
    formattedItems = self.getBasicPages()
    self.events = []
    print(formattedItems)
    #print(self.events)
    for event_page in range(len(formattedItems)):
      self.events.append({"<:prevpg:780564661275852890>": (self.pgPv, None),
                      "<:nextpg:780564809296904233>": (self.pgNx, None)})
      for item in formattedItems[event_page]:
        self.events[-1].update({MinecraftCommands.toEmoji(item): (self.transferItems, item)})
    #print(self.events)


  def inInventory(self, player, item):
    player_items = list(player.inventory.keys())
    if item in player_items:
      return player.inventory[item]
    return 0

  async def transferItems(self, item):
    player = MinecraftCommands.getPlayerData(self.ctx.author.id)
    otherPlayer = MinecraftCommands.getPlayerData(self.other.id)
    if self.inInventory(player, item) > 0:
      player.inventory[item] -= 1
      otherPlayer.inventory.update({item: otherPlayer.inventory.get(item, 0) + 1})
      MinecraftCommands.savePlayerData(self.ctx.author.id, player)
      MinecraftCommands.savePlayerData(self.other.id, otherPlayer)
    
    #  reinitializing player nesisary for running Emb func and Event func successfully
    self.player = MinecraftCommands.getPlayerData(self.ctx.author.id)
    self.otherPlayer = MinecraftCommands.getPlayerData(self.other.id)
    self.listen_reacts = []
    self.genTradeEmbs()
    self.genPageEvents()
    for event in self.events:
      pg_reacts = []
      for emoji in event.keys():
        pg_reacts.append(emoji)
      self.listen_reacts.append(pg_reacts)
    await self.msg.edit(embed=self.embeds[self.pg])
    



class Inventory(Book):

  def __init__(self, ctx):
    embeds = [self.generateItemPage(ctx), self.generateToolPage(ctx)]
    super().__init__(ctx, embeds, events=[{}, {"<:jay:780571254355656746>": (self.refreshInv, None)}])
    self.player = MinecraftCommands.getPlayerData(ctx.author.id)
    # jay emote is just a placeholder for an up arrow


  async def refreshInv(self):
    hand = self.player.inHand
    self.player.tools.append(hand)
    self.player.inHand = self.player.tools.pop(0)
    MinecraftCommands.savePlayerData(self.ctx.author.id, self.player)
    self.embeds = [self.generateItemPage(self.ctx), self.generateToolPage(self.ctx)]
    await self.msg.edit(embed=self.embeds[self.pg])
    

  def generateItemPage(self, ctx):
    player = MinecraftCommands.getPlayerData(ctx.author.id)
    inv = player.inventory
    embedItems = Embed(title=f"{ctx.author.name}'s Inventory <:bundle:780992430257340420>", color=0x00ff00)
    embedItems.set_footer(text="Page 1/2") 
    for item in inv.keys():
      embedItems.add_field(name=f"{MinecraftCommands.toEmoji(item)}  *  {inv[item]}",value="\~\~\~\~\~\~\~\~\~", inline=False)
    return embedItems


  def generateToolPage(self, ctx):
    player = MinecraftCommands.getPlayerData(ctx.author.id)
    tools = player.tools
    embedTools = Embed(title=f"{ctx.author.name}'s Inventory <:toolss:780992253081813062>", color=0x00ff00)
    embedTools.set_footer(text="Page 2/2")
    embedTools.add_field(name=f"Current Tool in hand:\n{MinecraftCommands.toEmoji(player.inHand.name)} ({player.inHand.durability}/{player.inHand.maxDurability})",value="\~\~\~\~\~\~\~\~\~", inline=False)
    for tool in tools:
      embedTools.add_field(name=f"{MinecraftCommands.toEmoji(tool.name)} ({tool.durability}/{tool.maxDurability})",value="\~\~\~\~\~\~\~\~\~", inline=False)
    return embedTools



class Crafting(Book):
  def __init__(self, ctx, player):
    self.update_pages = None
    self.ctx = ctx
    self.user_id = ctx.author.id
    self.bot = ctx.bot
    self.player = player
    self.pg = 0
    self.listen_reacts = []
    self.reacts = []


    self.recipes = {  # name: [item return quantity, {dictionary of ingredients} ]
      "wooden_pickaxe": [1, {"planks": 3, "stick": 2}],
      "stone_pickaxe": [1, {"cobblestone": 3, "stick": 2}],
      "iron_pickaxe": [1, {"iron_ingot": 3, "stick": 2}],
      "diamond_pickaxe": [1, {"diamond": 3, "stick": 2}],
      "planks": [4, {"oak_log": 1}],
      "stick": [4, {"planks": 2}],
      "diamond_block": [1, {"diamond": 9}],
      "diamond": [9, {"diamond_block": 1}],
      "redstone_block": [1, {"redstone_dust": 9}],
      "redstone_dust": [9, {"redstone_block": 1}]
    }
    self.tool_list = [
      "wooden_pickaxe",
      "stone_pickaxe",
      "iron_pickaxe",
      "diamond_pickaxe"
    ]
    self.item_list = [
      "planks",
      "stick",
      "diamond_block",
      "diamond",
      "redstone_dust",
      "redstone_block"
    ]
    self.create()

  
  async def craft(self, item):
    recipe = self.recipes[item][1]
    for resource_needed, quantity_needed in recipe.items():
      if not self.inPlayerInventory(resource_needed, quantity_needed):
        return
    for resource, quantity in recipe.items():
      self.player.inventory[resource] -= quantity
    amount = self.recipes[item][0]
    if item in self.item_list:
      self.player.inventory.update({item: self.player.inventory.get(item, 0) + 1 * amount})
      MinecraftCommands.savePlayerData(self.ctx.author.id, self.player) 
    elif item in self.tool_list and len(self.player.tools) < 9:
      self.player.tools.append(Tool(item, Tool.getToolDurability(item), Tool.getToolLevel(item)))
      MinecraftCommands.savePlayerData(self.ctx.author.id, self.player)
    self.listen_reacts = []
    self.create()
    for event in self.events:
      pg_reacts = []
      for emoji in event.keys():
        pg_reacts.append(emoji)
      self.listen_reacts.append(pg_reacts)
    await self.pgSet(self.pg)



  def inPlayerInventory(self, item, quantity):  # checks if an item of a certain quantity is in the user's inventory
    inv = self.player.inventory
    for k, v in inv.items():
      if item == k and quantity <= v:
        return True
    return False


  def getCraftableItems(self):  # returns a list of items the player can craft
    craftableItems = []   
    for item, resources in self.recipes.items():
      resource = resources[1]
      canCraft = False
      for k, v in resource.items():
        if not self.inPlayerInventory(k, v):
          canCraft = False
          break
        else:
          canCraft = True
      if canCraft:
        craftableItems.append(item)

    return craftableItems


  def createPages(self):
    self.pages = []
    crft = self.getCraftableItems()
    for i in range(len(crft) // 3): # the number of pages
      self.pages.append(crft[i*3:i*3+3]) # getting full pages
    if not len(crft) % 3 == 0:
      self.pages.append(crft[(len(crft)%3)*-1:]) # getting half page 
    

  def createEmbedPages(self): 
    print("created embed pages")
    self.embeds = []
    total_pages = len(self.pages)
    print(total_pages)
    print(self.pages)
    for page in self.pages:
      embed = Embed(title=f"{self.ctx.author.name}'s Crafting <:CraftingTable:780942061942865920>", color=0x00ff00)
      crnt_page = self.pages.index(page)
      print(crnt_page)
      embed.set_footer(text=f"Page {crnt_page+1}/{total_pages}",)
      for item in self.pages[crnt_page]:
        # writing the ingredient text
        ingredients_text = ""
        for ingredient, amount in self.recipes[item][1].items():
          ingredients_text += f"{MinecraftCommands.toEmoji(ingredient)} × {amount}"
        ingredients_text = "**[** " + ingredients_text + " **]**"
        # writing the recipie output
        nm = f"__{MinecraftCommands.toEmoji(item)} × {self.recipes[item][0]}__"
        # saving it all
        embed.add_field(
          name=nm,
          value=ingredients_text, 
          inline=True)
      self.embeds.append(embed)

      
  def createEventPages(self):
    print("created event pages")
    self.events = []
    # creating basic arrow objects
    arrow_events = {"<:prevpg:780564661275852890>": (self.pgPv, None),
                    "<:nextpg:780564809296904233>": (self.pgNx, None)}
    # adding items
    for page in self.pages:
      event = {}
      event.update(arrow_events)
      for item in page:
        #print(item)
        emoji = MinecraftCommands.toEmoji(item)
        func = self.craft
        arg = item
        event.update({emoji:(func, arg)})
      self.events.append(event)


  def create(self):
    self.createPages()
    self.createEmbedPages()
    self.createEventPages()



def setup(bot):
  minecraft = MinecraftCommands(bot)

  # loop commands
  
  # add to cogs
  bot.add_cog(minecraft)
