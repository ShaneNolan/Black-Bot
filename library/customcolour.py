import json
import os
import discord
from library import utilities

#Default Config for new Server
dataFirstTime = {
  "customColourGroup": "everyone",
  "donateAmount": 4.99
}

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
    configData = await utilities.LoadJson(config)

    if await utilities.CheckRole(message.author, configData["customColourGroup"]):
        #Check if the user has a custom colour role.
        rolename = str(message.author)[:-5]
        role = ""
        numRoles = 0
        for server in client.servers:
            if server == message.server:
                numRoles = len(server.roles)
                for roles in server.roles:
                    if(roles.name == rolename):
                        role=roles
                break

        #If they do have a role update their custom colour.
        if role != "":
            colour = discord.Colour(int(message.content[message.content.index('#')+1:], 16))
            await client.edit_role(message.server, role=role, colour=colour)
            await client.send_message(message.channel, "%s has changed their colour! :eggplant:" % (message.author.mention))
        #Else create their custom colour role.
        else:
            newRole = await client.create_role(message.server, permissions=discord.Permissions.none(), name=rolename)
            await client.move_role(message.server, newRole, numRoles)
            await client.add_roles(member, newRole)
    else:
        await client.send_message(message.author, "You do not have permission to set a custom colour. You need to be of rank \"%s\" to have a custom colour. :frowning:" % (configData["customColourGroup"]))
