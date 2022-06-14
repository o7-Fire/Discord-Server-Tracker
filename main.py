import discord

TOKEN = ""
client = discord.Client()
""" todo stop procrastinating and finish this
servertotrack = {}
with open("server-data.txt", "r+") as f:
	for line in f.read().split("\n"):
		linfo = line.split(" ")
		infotosave = {}
		for i in range(len(linfo) - 1):
		
		servertotrack[linfo[0]] = infotosave
"""

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
		
		for category in guildtocopy.categories:
			newcategory = await newguild.create_category(category.name)
			for channel in category.channels:
				await newguild.create_text_channel(channel.name, category=newcategory)
				
	if message.content.startswith("exec"):
		toexec = message.content.replace("exec\n", "", 1)
		await message.channel.send(exec(toexec))

client.run(TOKEN)
