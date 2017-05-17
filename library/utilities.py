import json

#Check if the user is an administrator.
async def checkAdmin(person):
    for r in person.roles:
        if r.permissions.administrator:
            return True
    return False

#Checks if a specific user has a role.
async def CheckRole(person, role):
    if role == "everyone":
        return True

    for r in person.roles:
        if r.name == role:
            return True
    return False

#Load a JSON file.
async def LoadJson(location):
    with open(location, 'rt') as f:
        configData = json.load(f)
    f.close()
    return configData
