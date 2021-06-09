import discord
from discord.ext import commands
import os
import asyncio
import json
from decouple import config
import os


token = config("TOKEN")
intents = discord.Intents.default()
intents.members = True
intents.presences = True
emojisOn = False
MUTED_ROLE_ID = 850328365260734474
GUILD_ID = 843823778755641344
user_db = []

client = commands.Bot(command_prefix='t.', case_insensitive=True, intents=intents)
client.remove_command("help")

@client.event
async def on_ready():
  await client.change_presence(status=discord.Status.online, activity=discord.Game('With Miko Chan'))
  print('Bot is Online.')

@client.command()
async def help(ctx):
  try:
    h = discord.Embed(
      title="NEED HELP?",
      description="Bot Creator: **ASHISH**",
      color=0x13fc03,
    )
    h.add_field(
      name="__ABOUT__", 
      value=f"\nPrefix : `t.`\nTox Kun is a Discord Bot created to help people complete a detox effectively. You can start your detox timer using Tox Kun and Tox Kun will change your nickname to `[DETOX]user` and will mute you from the server for the time given.", 
      inline=False
    )
    h.add_field(
      name="__HOW TO USE__",
      value=f"The time specified should be atleast in hours or Tox Kun will not work. Here is how to use the command: `t.detox 1h`. This will start a detox timer for 1 hour. To start detox for days use `d` in place of `h` like `t.detox 1d` will start a detox timer for 1 day.",
      inline=False
    )
    h.add_field(
      name="__COMMANDS__",
      value=f"`detox (time)` Starts detox timer for the user.",
      inline=False
    )

    await ctx.send(embed=h)
  except Exception as e:
    print(e)

  @client.command()
  async def source(ctx):
    await ctx.send("https://replit.com/@AshKun/tox-chan")  

def add_member(member):
  user_db.append(member)

def remove(member):
  user_db.remove(member)      

@client.command()
async def detox(ctx, time=None):
  if not time:
    await ctx.send("You must mention a time!")
  else:
    member = ctx.author  
    old_nick = member.display_name
    new_nick = "[DETOX]" + old_nick
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    time_convert = {"s":1, "m":60, "h":3600,"d":86400}
    tempmute= int(time[0]) * time_convert[time[-1]]
    await member.edit(nick=new_nick)
    await member.add_roles(role)
    user_db.append(ctx.author.id)
    print(user_db)
    detox_embed = discord.Embed(title="Your detox starts now!", description=f"{member.mention} is on detox for {time}\nGood Luck!", color=0x13fc03)
    await ctx.send(embed=detox_embed)
    await asyncio.sleep(tempmute)
    await member.remove_roles(role)
    undetox_embed = discord.Embed(title="Your detox has ended!", description=f"{member.mention} you were on detox for {time}\nGreat work!", color=0x13fc03)
    await ctx.send(embed=undetox_embed)
    await member.edit(nick=old_nick)

@client.event
async def on_message(message):
  await client.process_commands(message)
  if message.author.bot:
    return
  for mention in message.mentions:
    if mention.id in user_db:
      await message.channel.send(
        f"{message.author.mention}, **{mention}** is on DETOX! Do not ping them!", delete_after=25,)

client.run(token)     
