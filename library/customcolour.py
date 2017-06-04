import json
import os
import discord
from library import utilities

#Custom Colour Feature
async def CustomColour(client, message):
    config = "database/servers/" + str(message.server.id) + ".json"
    #Check if new server, if so create their config.
    if not os.path.exists(config):
        with open(config, 'w') as f:
            json.dump(dataFirstTime, f)
            print("Created default server configuration:%s." % (config))
        f.close()

    #Get server config data.
    configData = await utilities.loadJSON(config)

    if await utilities.checkRole(message.author, config["customColourRole"]):
        #Check if the user has a custom colour role.
        rolename = str(message.author)[:-5]
        role = await utilities.getRole(client, message, rolename)

        #If they dont have a role for a custom colour create one.
        if role is None:
            newRole = await utilities.createRole(client, message, rolename)
            await client.add_roles(member, newRole)
            role = await utilities.getRole(client, message, rolename)

        #Update/Set their custom colour.
        colour = discord.Colour(int(message.content[message.content.index('#')+1:], 16))
        await client.edit_role(message.server, role=role, colour=colour)
        await client.send_message(message.channel, "%s has changed their colour! :eggplant:" % (message.author.mention))
    else:
        await client.send_message(message.author, "You do not have permission to set a custom colour. You need to be of rank \"%s\" to have a custom colour. :frowning:" % (configData["customColourRole"]))
