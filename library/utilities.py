import json
import discord
import os
import csv

#Check if the user is an administrator.
async def checkAdmin(person):
    for r in person.roles:
        if r.permissions.administrator:
            return True
    return False

#Checks if a specific user has a role.
async def checkRole(person, role):
    if role == "everyone":
        return True

    for r in person.roles:
        if r.name == role:
            return True
    return False

#Load a JSON file.
async def loadJSON(location):
    with open(location, 'rt') as f:
        configData = json.load(f)
    f.close()
    return configData

#Overwrite a JSON file.
async def overwriteJSON(location, newConfig):
    os.remove(location)
    with open(location, 'w') as f:
        json.dump(newConfig, f)
    f.close()

#Load a CSV file.
async def loadCSV(location):
    with open(location, 'rt') as f:
        donateData = csv.reader(f)
        return reversed(list(donateData))

#Get a users specific role.
async def getRole(client, message, roleName):
    for server in client.servers:
        if server == message.server:
            for role in server.roles:
                if roleName == role.name:
                    return role
    return 0

#Create a role.
async def createRole(client, message, rolename):
    for server in client.servers:
        if server == message.server:
            numRoles = len(server.roles)

    newRole = await client.create_role(message.server, permissions=discord.Permissions.none(), name=rolename)
    await client.move_role(message.server, newRole, numRoles)
    return newRole
