import discord
from discord.ext import commands, tasks
import os
import asyncio
import json
from decouple import config
import os
import pyrebase

token = config("TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.presences = True
MUTED_ROLE_ID = 785030970050740236
GUILD_ID = 785024897863647282
user_db = []
time_refresh = 1
GENERAL_ID = 785024897863647285

firebase = pyrebase.initialize_app(json.loads(config("firebaseConfig")))
db = firebase.database()

def create(user: int, message: str):
  db.child("DETOX_USER").child(user).set(
        {"DETOX_MESSAGE": message}
  )

def check(user: int):
  member = db.child("DETOX_USER").child(user).get().val()
  if member == None:
    return False
  else:
    return True  

def remove(user: int):
  db.child("DETOX_USER").child(user).remove()    

def return_message(user: int):
  note = db.child("DETOX_USER").child(user).child("DETOX_MESSAGE").get().val()
  return note

client = commands.Bot(command_prefix='t.', case_insensitive=True, intents=intents)
client.remove_command("help")

@client.event
async def on_ready():
  await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name='Tokyo Revengers'))
  print('Bot is Online.') 

@client.command()
async def help(ctx):
    h = discord.Embed(
      title="NEED HELP?",
      description="Bot Creator: **ASHISH**",
      color=0x13fc03,
    )
    h.add_field(
      name="__ABOUT__", 
      value=f"\nPrefix : `t.`\nTox Kun is a Discord Bot created to help people complete a detox effectively. You can start your detox timer using Tox Kun and Tox Kun will change your nickname to `[DETOX]user` and will mute you from the server until you stop it.", 
      inline=False
    )
    h.add_field(
      name="__HOW TO USE__",
      value=f"To mute yourself you will have to send the command `t.detox (your note)` and Tox kun will mute you from the server. When you want to unmute yourself send teh command `t.stop` in my DM. Make sure that you are accepting DMs from server members or else Usui will not be able to unmute you!",
      inline=False
    )
    h.add_field(
      name="__COMMANDS__",
      value=f"`detox` Starts detox timer for the user and mutes them.\n`stop` Stops your detox timer and unmutes them.",
      inline=False
    )
    h.add_field(
      name="__TO STOP TIMER__",
      value=f"To stop timer send the command `t.stop` in my DM.",
      inline=False
    )
    h.add_field(
      name="__SOURCE CODE__",
      value="`t.source`",
      inline=False
    )

    await ctx.send(embed=h)

@client.command()
async def source(ctx):
  await ctx.send("https://github.com/AsheeshhSenpai/tox-kun")  

@client.command()
async def embed(ctx, *, title):
  if ctx.author.id == 784363251940458516:
    guild = client.get_guild(GUILD_ID)
    GENERAL= guild.get_channel(GENERAL_ID)
    await ctx.send(" Please send description.")
    desc = await client.wait_for("message", check=lambda message: message.author == ctx.author)
    description = str(desc.content)
    emb = discord.Embed(title=f"{title}", description=f"{description}")
    await GENERAL.send(embed=emb)
  else:
    await ctx.send("You don't have perms to use this cmd!")
  
@client.command()
async def detox(ctx, *, message = None):
  if check(ctx.author.id) == False:
    if message == None:
      message = "None"
    member = ctx.author  
    old_nick = member.display_name
    new_nick = "[DETOX]" + old_nick
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    detox_embed = discord.Embed(title="Your detox starts now!", description=f"{member.mention} is on detox. To stop your detox timer send `t.stop` in my DM and make sure that you are accepting DM from server members.\nGood Luck!", color=0x13fc03)
    await ctx.send(member.mention, embed=detox_embed)
    create(ctx.author.id, message)
    user_db.append(ctx.author.id)
    await member.edit(nick = new_nick)
    await member.add_roles(role)
  else:
    await ctx.send(f"{ctx.author.mention} You are already on detox!")

@client.command()
async def stop(ctx):
  guild = client.get_guild(GUILD_ID)
  member = guild.get_member(ctx.author.id)
  if check(member.id) == True:
    nick = member.display_name
    new_nick = nick[7:]
    role = discord.utils.get(guild.roles, name="Muted")
    await member.remove_roles(role)
    remove(member.id)
    if nick.startswith("[DETOX]"):
      await member.edit(nick=new_nick)
    undetox_embed = discord.Embed(title="Your detox timer has been stopped!", description=f"{member.mention} you are unmuted now.", color=0x13fc03)
    await ctx.send(member.mention, embed=undetox_embed)  
  else:
    await ctx.send(f"{member.mention} You are currently not on detox! Send `t.detox` to start detox.")
 

@client.event
async def on_message(message):
  await client.process_commands(message)
  if message.author.bot:
    return
  for mention in message.mentions:
    if check(mention.id) == True:
      note = return_message(mention.id)
      await message.channel.send(
        f"{message.author.mention}, **{mention}** is on DETOX! Do not ping them!\nNOTE: **{note}**", delete_after=25,)

client.run(token)     
 
