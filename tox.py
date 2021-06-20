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
TIME_REFRESH = 1

firebase = pyrebase.initialize_app(json.loads(config("firebaseConfig")))
db = firebase.database()

def create(user: int, time: int):
  db.child("DETOX_USER").child(user).set(
        {"DETOX_TIME": time}
  )

def check(user: int):
  member = db.child("DETOX_USER").child(user).get().val()
  if member == None:
    return False
  else:
    return True  

def remove(user: int):
  db.child("DETOX_USER").child(user).remove()    

def add_time(user: int, time: int):
  detox_user = db.child("DETOX_USER").child(user).get().val()
  if detox_user == None:
    create(user, time)
  else:  
    auth = db.child("DETOX_USER").child(user).child("DETOX_TIME").get()
    t = auth.val()
    t = t + time
    db.child("USER_TIME").child(user).update({"DETOX_TIME": t})

def return_time(user: int):
  time = db.child("DETOX_USER").child(user).child("DETOX_TIME").get().val()
  hour = int(time/60)
  min = time%60
  return hour, min

client = commands.Bot(command_prefix='t.', case_insensitive=True, intents=intents)
client.remove_command("help")

@client.event
async def on_ready():
  await client.change_presence(status=discord.Status.online, activity=discord.Game('With Miko Chan'))
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
      value=f"To mute yourself you will have to send the command `t.detox` and Tox kun will mute you from the server. When you want to unmute yourself send teh command `t.stop` in `#Bot-Commands` channel.",
      inline=False
    )
    h.add_field(
      name="__COMMANDS__",
      value=f"`detox` Starts detox timer for the user and mutes them.\n`stop` Stops your detox timer and unmutes them.",
      inline=False
    )
    h.add_field(
      name="__TO STOP TIMER__",
      value=f"To stop timer send the command `t.stop` in `#Bot-Commands` channel.",
      inline=False
    )

    await ctx.send(embed=h)

@client.command()
async def source(ctx):
  await ctx.send("https://replit.com/@AshKun/tox-chan")  


@client.command()
async def detox(ctx):
  if check(ctx.author.id) == False:
    member = ctx.author  
    old_nick = member.display_name
    new_nick = "[DETOX]" + old_nick
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    await member.edit(nick = new_nick)
    await member.add_roles(role)
    detox_embed = discord.Embed(title="Your detox starts now!", description=f"{member.mention} is on detox. To stop your detox timer send `t.stop`.\nGood Luck!", color=0x13fc03)
    await ctx.send(member.mention, embed=detox_embed)
    create(ctx.author.id)
    user_db.append(ctx.author.id)
  else:
    await ctx.send(f"{ctx.author.mention} You are already on detox!")

@client.command()
async def stop(ctx):
  member = ctx.author
  if check(member.id) == True:
    nick = member.display_name
    new_nick = nick[7:]
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    await member.remove_roles(role)
    remove(ctx.author.id)
    user_db.remove(ctx.author.id)
    hour, minute = return_time(ctx.author.id)
    if nick.startswith("[DETOX]"):
        await member.edit(nick=new_nick)
    undetox_embed = discord.Embed(title="Your detox timer has been stopped!", description=f"{member.mention} you were on detox for {hour} hour and {minute} minutes.", color=0x13fc03)
    await ctx.send(member.mention, embed=undetox_embed)  
  else:
    await ctx.send(f"{member.mention} You are currently not on detox! Send `t.detox` to start detox.")

@tasks.loop(seconds=10)
async def on_detox():
  users = db.child("DETOX_USER").get()
  for user in users.each():
    if user in user_db:
      return
    else:
      user_db.append(user)  

@tasks.loop(minutes=1)
async def refresh_time():
  for user in user_db:
    if check(user) == True:
      add_time(user, TIME_REFRESH)

@client.event
async def on_message(message):
  await client.process_commands(message)
  if message.author.bot:
    return
  for mention in message.mentions:
    if check(mention.id) == True:
      await message.channel.send(
        f"{message.author.mention}, **{mention}** is on DETOX! Do not ping them!", delete_after=25,)

client.run(token)     
 
