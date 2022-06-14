import discord

TOKEN = ""
client = discord.Client()
servertotrack = {}

def updatelist():
	with open("server-data.txt", "r+") as f:
		for line in f.read().split("\n"):
			if not line.strip(): continue #thank you one line code
			linfo = line.split(" ")
			infotosave = {}
			for i in range(len(linfo) - 1):
				if i % 2 == 0:
					infotosave[linfo[i]] = linfo[i+1]
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
				
		with open("server-data.txt", "w+") as f:
			f.write(messagetowrite + "\n")
		updatelist()
				
	if message.content.startswith("exec"):
		toexec = message.content.replace("exec\n", "", 1)
		await message.channel.send(exec(toexec))
	if message.content == "tdo":
		print("do nothing")

client.run(TOKEN)
