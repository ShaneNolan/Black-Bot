import discord
from library import btc
from library import donation
from library import customcolour
from library import utilities

client = discord.Client()

#Custom Prefix e.g. !help
prefix = '!'

@client.event
async def on_ready():
  print('Logged in as: %s#%s' % (client.user.name, client.user.id))


@client.event
async def on_message(message):
    message.content.strip()
    if(len(message.content) > 2):
        #Check to see if its a bot request.
        if message.content[0] == prefix:
            await client.delete_message(message)
            message.content = message.content[len(prefix):]
            print("Request received by: %s on server: %s(%s) requesting: %s." % (message.author, message.server, message.server.id, message.content))

            #Display developer.
            if message.content == 'developer':
                await client.send_message(message.channel, 'Developed by dildo#9822')

            #Setup WIP.
            elif message.content == 'setup' and await utilities.checkAdmin(message.author):
                print("WIP")

            #Custom Colours.
            elif 'color' in message.content or 'colour' in message.content:
                await customcolour.CustomColour(client, message)

            #Bitcoin Donations.
            elif message.content == 'donate':
                await donation.Donate(client, message)


if __name__ == '__main__':
    client.run("tokenhere")
