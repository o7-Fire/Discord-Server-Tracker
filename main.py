import discord
from discord import Webhook, RequestsWebhookAdapter
import time
import os
import random
import string
import json

TOKEN = ""
dataminingfeatureenabled = True  # if you want to data mine

client = discord.Client()
webhookadapter = RequestsWebhookAdapter()
servertotrack = {}


def save_data(author, content, serverid, attachmentlinks=[], edited=False):
	path = f"./data/{str(serverid)}.txt"
	if not os.path.exists(path):
		with open(path, "w+") as f:
			donothingvalue = 0
	tosave = {
		"id": str(author.id),
		"strname": str(author),
		"displayname": author.display_name,
		#"avatar": str(author.avatar_url),
		"edited": edited,
		#"status": author.status,
		"content": content,
		"attachments": attachmentlinks,
	}
	with open(path, "a+") as f:
		json.dump(tosave, f)
		f.write("\n")

def save_profile(author, savetype):
	path = f"./data/profile_data.txt"
	if not os.path.exists(path):
		with open(path, "w+") as f:
			donothingvalue = 0
	tosave = {
		"save_type": savetype,
		"id": str(author.id),
		"strname": str(author),
		"displayname": author.display_name,
		"avatar": str(author.avatar_url),
		"activity": str(author.activity),
		"status": str(author.raw_status),
	}
	with open(path, "a+") as f:
		json.dump(tosave, f)
		f.write("\n")
	
def updatelist():
	with open("server-data.txt", "r") as f:
		for line in f.read().split("\n"):
			if not line.strip(): continue  # thank you one line code
			linfo = line.split(" ")
			infotosave = {}
			for i in range(len(linfo) - 2):
				if i % 2 == 0:
					infotosave[linfo[i + 1]] = linfo[i + 2]
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

async def message_handler(message, edited=False):
	serverval = servertotrack[str(message.guild.id)]
	channelwebhook = serverval[str(message.channel.id)]
	webhook = Webhook.from_url(channelwebhook, adapter=webhookadapter)
	if message.embeds:  # bots only
		webhook.send(username=str(message.author), avatar_url=message.author.avatar_url, content=message.content,
		             embeds=message.embeds)
	elif message.attachments:
		files = []
		filestodelete = []
		filelinks = []
		for attachment in message.attachments:
			if attachment.size < 8000000:
				randomname = ''.join(
					random.choice(string.ascii_lowercase + string.ascii_uppercase) for i in range(10))
				attachname = attachment.filename
				thenewname = f"./temp/{attachname.split('.')[0]}{randomname}.{attachname.split('.')[1]}"
				await attachment.save(fp=thenewname)
				files.append(discord.File(thenewname))
				filestodelete.append(thenewname)
				filelinks.append(attachment.url)
		webhook.send(username=str(message.author), avatar_url=message.author.avatar_url, content=message.content,
		             files=files)
		if dataminingfeatureenabled:
			save_data(message.author, message.content, message.guild.id, filelinks, edited)
		files = []  # deletes it
		for f in filestodelete:
			os.remove(f)
	else:
		webhook.send(username=str(message.author), avatar_url=message.author.avatar_url, content=message.content)
		if dataminingfeatureenabled:
			save_data(message.author, message.content, message.guild.id, edited=edited)
			
@client.event
async def on_ready():
	print(f'{client.user} has connected to Discord!')

"""
@client.event
async def on_member_update(before, after):
	save_profile(after, "on_member_update")
"""

@client.event
async def on_message_edit(before, after):
	if str(after.guild.id) in servertotrack:
		await message_handler(after, True)
	
@client.event
async def on_message(message):
	# if message.author.bot:
	#	return
	# this handles the message copying process
	if str(message.guild.id) in servertotrack:
		await message_handler(message)
	
	# after this line only client can run
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
			# print(f"{str(channel.id)} {webhook.url} ")
		
		with open("server-data.txt", "a+") as f:
			f.write(messagetowrite + "\n")
		time.sleep(5)
		updatelist()
	
	if message.content.startswith("exec"):
		toexec = message.content.replace("exec\n", "", 1)
		await message.channel.send(exec(toexec))
	if message.content == "cpi":
		await client.change_presence(status=discord.Status.invisible)
	if message.content == "cpo":
		await client.change_presence(status=discord.Status.online)


client.run(TOKEN)
