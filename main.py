import discord
import time
import os
import random
import string
from discord import Webhook, RequestsWebhookAdapter

TOKEN = ""
client = discord.Client()
webhookadapter = RequestsWebhookAdapter()
servertotrack = {}

def updatelist():
	with open("server-data.txt", "r") as f:
		for line in f.read().split("\n"):
			if not line.strip(): continue #thank you one line code
			linfo = line.split(" ")
			infotosave = {}
			for i in range(len(linfo) - 2):
				if i % 2 == 0:
					infotosave[linfo[i+1]] = linfo[i+2]
			servertotrack[linfo[0]] = infotosave
updatelist()

async def createbasedontype(channel, guild, category):
	if channel.type == discord.ChannelType.text:
		return await guild.create_text_channel(channel.name, category=category)
	elif channel.type == discord.ChannelType.voice:
		return await guild.create_voice_channel(channel.name, category=category)
	elif channel.type == discord.ChannelType.stage_voice:
		return await guild.create_voice_channel(channel.name, category=category)
	else:
		return await guild.create_text_channel(channel.name, category=category)
		
@client.event
async def on_ready():
	print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
	#if message.author.bot:
	#	return
	#this handles the message copying process
	if str(message.guild.id) in servertotrack:
		serverval = servertotrack[str(message.guild.id)]
		channelwebhook = serverval[str(message.channel.id)]
		webhook = Webhook.from_url(channelwebhook, adapter=webhookadapter)
		if message.embeds:
			webhook.send(username=str(message.author), avatar_url=message.author.avatar_url, content=message.content, embeds=message.embeds)
		elif message.attachments:
			files = []
			filestodelete = []
			for attachment in message.attachments:
				if attachment.size < 8000000:
					randomname = ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase) for i in range(10))
					attachname = attachment.filename
					thenewname = f"./temp/{attachname.split('.')[0]}{randomname}.{attachname.split('.')[1]}"
					await attachment.save(fp=thenewname)
					files.append(discord.File(thenewname))
					filestodelete.append(thenewname)
			webhook.send(username=str(message.author), avatar_url=message.author.avatar_url, content=message.content, files=files)
			files = [] #deletes it
			for f in filestodelete:
				os.remove(f)
		else:
			webhook.send(username=str(message.author), avatar_url=message.author.avatar_url, content=message.content)
			
	#after this line only client can run
	if message.author.id != client.user.id:
		return
	
	if message.content.startswith("copyserver "):
		idtocopy = int(message.content.replace("copyserver ", ""))
		guildtocopy = client.get_guild(idtocopy)
		newguild = await client.create_guild(guildtocopy.name)
		
		messagetowrite = f"{str(guildtocopy.id)} "
		for category in guildtocopy.categories:
			newcategory = await newguild.create_category(category.name)
			for channel in category.channels:
				newchannel = await createbasedontype(channel, newguild, newcategory)
				if newchannel.type == discord.ChannelType.text:
					webhook = await newchannel.create_webhook(name="webhook name here")
					messagetowrite += f"{str(channel.id)} {webhook.url} "
					print(f"{str(channel.id)} {webhook.url} ")
				
		with open("server-data.txt", "a+") as f:
			f.write(messagetowrite + "\n")
		print(messagetowrite)
		time.sleep(5)
		updatelist()
				
	if message.content.startswith("exec"):
		toexec = message.content.replace("exec\n", "", 1)
		await message.channel.send(exec(toexec))
	if message.content == "tdo":
		print("do nothing")

client.run(TOKEN)
