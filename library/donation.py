import os
import csv
import urllib
import urllib.request
from bs4 import BeautifulSoup
from library import utilities
from library import btc

#Donation Feature
async def Donate(client, message):
    donationDB = "database/donations/" + str(message.server.id) + ".csv"

    config = await utilities.loadJSON("database/servers/" + str(message.server.id) + ".json")
    with open(donationDB, 'rt') as f:
        reader = csv.reader(f)
        #A temp list is used to store clients donations incase of a update -> donation received.
        temp = []
        found = False
        updated = False

        for row in reader:
            if not row:
                continue
            #If a donation address already exists for the request user.
                #Check if they have donated.
                #Display previously generated Bitcoin address that doesn't have a donation.
            elif row[0] == str(message.author) and row[3] == "0":
                found = True
                html = urllib.request.urlopen("https://blockchain.info/address/" + row[2] + "?currency=USD")
                soup = BeautifulSoup(html, "html.parser")
                amount = soup.find(id="final_balance")

                #Donation received.
                if float(amount.text[2:]) >= config["donateAmount"]:
                    updated = True
                else:
                    await client.send_message(message.author, "To donate to `%s`, send an amount greater than $`%s` to: ```%s```\nThank you :slight_smile:" % (message.server, config["donateAmount"], row[2]))
                temp.append(row)
            else:
                temp.append(row)
        f.close()

        #Check for update -> Donation received.
        if updated == True:
            os.remove(donationDB)
            dRole = await utilities.getRole(client, message, config["donateRole"])

            if dRole == 0:
                dRole = await utilities.createRole(client, message, config["donateRole"])

            await client.add_roles(message.author, dRole)
            await client.send_message(message.author, 'We have received your donation to %s! You have received the role "%s".:hugging:\nThank you so much, we appreicate the support. :heart:' % (message.server, config["donateRole"]))
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

            await client.send_message(message.author, "To donate to `%s`, send an amount greater than $`%s` to: ```%s```\nThank you :slight_smile:" % (message.server, config["donateAmount"], address_encoded))

#Send Recent Donations.
async def Donations(client, message):
    #Get Donation data.
    donateData = await utilities.loadCSV("database/donations/" + str(message.server.id) + ".csv")

    await client.send_message(message.author, "```diff\n- Black Bot - Recent Donations -```\n")
    #Amount of recent donations to display.
    counter = 0
    maxCounter = message.content[7:]
    if not maxCounter:
        maxCounter = 5

    for row in donateData:
        if not row:
            continue
        if row[3] == "1":
            await client.send_message(message.author, "**Username:** `" + row[0] + "`\n" + "**Private Key:** `" + row[1] + "`\n" + "**Public Key:** `" + row[2] + "`\n\n")
            counter = counter + 1
        if counter == maxCounter:
            break
