import discord
import os
import json

from library import btc
from library import donation
from library import customcolour
from library import utilities
from library import music

client = discord.Client()

#Custom Prefix e.g. !help
prefix = '!'
MPlayer = music.Music(client)

@client.event
async def on_ready():
    print('Logged in as: %s#%s' % (client.user.name, client.user.id))

@client.event
async def on_server_join(self):
    #On server join, create their configs.
    donationDB = "database/donations/" + str(self.id) + ".csv"
    if not os.path.exists(donationDB):
        with open(donationDB, 'w') as f:
            print("Created donation database:%s." % (donationDB))
        f.close()

    #Default Config for new Server
    dataFirstTime = {
      "customColourGroup": "everyone",
      "donateRole": "none",
      "donateAmount": 4.99
    }
    config = "database/servers/" + str(self.id) + ".json"
    if not os.path.exists(config):
        with open(config, 'w') as f:
            json.dump(dataFirstTime, f)
            print("Created default server configuration:%s." % (config))
        f.close()

@client.event
async def on_message(message):
    message.content.lower().strip()
    if(len(message.content) > 2):
        #Check to see if its a bot request.
        if message.content[0] == prefix:
            global MPlayer
            await client.delete_message(message)
            message.content = message.content[len(prefix):]
            print("Request received by: %s on server: %s(%s) requesting: %s." % (message.author, message.server, message.server.id, message.content))

            #Display developer.
            if message.content == 'help':
                header = "```diff\n- Black Bot - Commands/Help -```\n"
                #Additional Admin Commands
                adminsc = """**Set Features:** `set donatorole rolename` `set donateamount amount` `set customcolourrole rolename`\n"""
                commands = """**Donate:** `!donate`\n**Custom Colour:** `!colour #hexcode`\n**Music Player:** `!play songname` `!pause` `!resume` `!skip` `!playing`
                ```html\nBlack Bot Version: Alpha 8.0\nReport any bugs to: dildo#9822.```"""

                if await utilities.checkAdmin(message.author):
                    await client.send_message(message.author, header + adminsc + commands)
                else:
                    await client.send_message(message.author, header + commands)

            #Custom Colours.
            elif 'color' in message.content or 'colour' in message.content:
                await customcolour.CustomColour(client, message)

            #Bitcoin Donations.
                #If Admin send details on recent donations.
                #Else send details on how to donate.
            elif 'donate' in message.content:
                if await utilities.checkAdmin(message.author):
                    await donation.Donations(client, message)
                else:
                    await donation.Donate(client, message)

            #Music Player Options.
            elif 'play' in message.content:
                await MPlayer.play(message, song = message.content)
            elif message.content == 'pause':
                await MPlayer.pause(message)
            elif message.content == 'resume':
                await MPlayer.resume(message)
            elif message.content == 'stop':
                await MPlayer.stop(message)
            elif message.content == 'skip':
                await MPlayer.skip(message)
            elif message.content == 'playing':
                await MPlayer.playing(message)


            #Server Config Modifications || Set Commands
            elif 'set' in message.content and await utilities.checkAdmin(message.author):
                message.content = message.content[4:]
                location = "database/servers/" + str(message.server.id) + ".json"
                config = await utilities.loadJSON(location)

                #Change DonateRole.
                if 'donatorrole' in message.content:
                    config["donateRole"] = message.content[11:]
                    await utilities.overwriteJSON(location, config)
                #Change DonateAmount.
                elif 'donateamount' in message.content:
                    config["donateAmount"] = float(message.content[13:])
                    await utilities.overwriteJSON(location, config)
                #Change CustomColourRole. e.g. everyone or just donators.
                elif 'customcolourrole' in message.content:
                    config["customColourRole"] = message.content[17:]
                    await utilities.overwriteJSON(location, config)


if __name__ == '__main__':
    client.run("token here")
