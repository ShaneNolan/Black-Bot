import json
import os
import discord
from library import utilities

#Custom Colour Feature
async def CustomColour(client, message):
    config = "database/servers/" + str(message.server.id) + ".json"

    #Get server config data.
    configData = await utilities.loadJSON(config)

    if await utilities.checkRole(message.author, configData["customColourRole"]):
        try:
            #If they dont have a role for a custom colour create one.
            if await utilities.getRole(message, str(message.author)) is None:
                role = await client.create_role(message.server, permissions=discord.Permissions.none(), name=str(message.author))
                await client.move_role(message.server, role, len(message.server.roles)-2)
                await client.add_roles(message.author, role)

            #Update/Set their custom colour.
            colour = discord.Colour(int(message.content[message.content.index('#')+1:], 16))
            await client.edit_role(message.server, role=await utilities.getRole(message, str(message.author)), colour=colour)
            await client.send_message(message.channel, "%s has changed their colour! :eggplant:" % (message.author.mention))
        except discord.errors.Forbidden:
            await client.send_message(message.channel, "I don't have sufficient privileges for this request, move my role to the top of the role list! :nerd:")
    else:
        await client.send_message(message.author, "You do not have permission to set a custom colour. You need to be of rank \"%s\" to have a custom colour. :frowning:" % (configData["customColourRole"]))
