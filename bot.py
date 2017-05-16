import discord
import os
import csv
import btc
import urllib
import urllib.request
from bs4 import BeautifulSoup

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
        #Check to see if bot request.
        if message.content[0] == prefix:
            message.content = message.content[len(prefix):]
            print("Request received by:%s on server:%s requesting:%s" % (message.author, message.server, message.content))

            #Display developer.
            if message.content == 'developer':
                await client.send_message(message.channel, 'Developed by dildo#9822')
                await client.delete_message(message)

            #Setup custom roles.
            elif message.content == 'setup' and str(message.author) == "dildo#9822":
                for server in client.servers:
                    if server == message.server:
                        roles = []
                        for r in server.roles:
                            roles.append(str(r))
                        for member in server.members:
                            rolename = str(member)[:-5]
                            #Create user role.
                            if rolename not in roles:
                                role = await client.create_role(message.server, permissions=discord.Permissions.none(), name=rolename)
                                await client.move_role(message.server, role, len(roles)-1)
                                await client.add_roles(member, role)
                                print ("%s was created successfully." % (rolename))
                            else:
                                print ("%s already exists." % (rolename))
                        break
                await client.delete_message(message)

            elif 'color' in message.content or 'colour' in message.content:
                colour = discord.Colour(int(message.content[message.content.index('#')+1:], 16))
                rolename = str(message.author)[:-5]
                role = ""

                #Check if the users role exists.
                for server in client.servers:
                    if server == message.server:
                        for roles in server.roles:
                            if(roles.name == rolename):
                                role=roles
                        break

                #If the role was found update it.
                if role != "":
                    await client.edit_role(message.server, role=role, colour=colour)
                    member = discord.utils.get(message.server.members, name=rolename)
                    await client.send_message(message.channel, '%s has changed their colour! :eggplant:' % (member.mention))
                    await client.delete_message(message)
                else:
                    print ("%s doesn't have a role. Do !setup to give them a role." % (message.author))

            elif message.content == 'donate':
                donationDB = str(message.server.id) + ".csv"
                if not os.path.exists(donationDB):
                    with open(donationDB, 'a') as f:
                        print("Created donation database:%s." % (donationDB))
                with open(donationDB, 'rt') as f:
                    reader = csv.reader(f)
                    #A temp list is used to store clients donations incase of a update -> donation received.
                    temp = []
                    found = False
                    updated = False

                    for row in reader:
                        if not row:
                            break
                        #If a donation address already exists for the request user.
                            #Check if they have donated.
                            #Display previously generated Bitcoin address that doesn't have a donation.
                        elif row[0] == str(message.author) and row[3] == "0":
                            found = True
                            html = urllib.request.urlopen("https://blockchain.info/address/" + row[2] + "?currency=USD")
                            soup = BeautifulSoup(html, "html.parser")
                            amount = soup.find(id="final_balance")

                            #Donation received.
                            if float(amount.text[2:]) >= 5:
                                updated = True
                            await client.send_message(message.author, 'To donate, send an amount greater than $4.99 to: ```%s```Thank you :slight_smile:' % (row[2]))
                            temp.append(row)
                        else:
                            temp.append(row)
                    f.close()

                    #Check for update -> Donation received.
                    if updated == True:
                        os.remove(donationDB)
                        await client.send_message(message.author, 'We have received your donation! Thank you so much, we appreicate the support. :heart:')
                        with open(donationDB, 'w') as csv_file:
                            writer = csv.writer(csv_file)
                            for item in temp:
                                #Update the database to confirm the donation.
                                if item[0] == str(message.author) and item[3] == "0":
                                    item = [item[0], item[1], item[2], "1"]
                                writer.writerow(item)

                    #Create a donation address.
                    if found == False:
                        #Create a Bitcoin Private Key.
                        private_key = btc.generateKey(btc.key_length)
                        priv_key = btc.privKeyToWIF(private_key, btc.wif_version_byte, btc.type_pub)

                        #Create a Bitcoin Public Key from Private Key.
                        public_key = btc.privateKeyToPublicKey(private_key)
                        address = btc.getAddressFromPublicKey(public_key, btc.version_byte)
                        address_encoded = btc.base58CheckEncoding(address)

                        #Write the new users donation address to the database.
                        with open(donationDB, 'a') as csv_file:
                            writer = csv.writer(csv_file)
                            data = [str(message.author), priv_key, address_encoded, "0"]
                            writer.writerow(data)

                        await client.send_message(message.author, 'To donate, send an amount greater than $4.99 to: ```%s```Thank you :slight_smile:' % (address_encoded))


if __name__ == '__main__':
    client.run("token")
