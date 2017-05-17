import os
import csv
import urllib
import urllib.request
from bs4 import BeautifulSoup
from library import utilities

#Donation Feature
async def Donate(client, message):
    donationDB = "database/donations/" + str(message.server.id) + ".csv"
    if not os.path.exists(donationDB):
        with open(donationDB, 'w') as f:
            print("Created donation database:%s." % (donationDB))
        f.close()
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

                config = await utilities.LoadJson("database/servers/" + str(message.server.id) + ".json")
                #Donation received.
                if float(amount.text[2:]) >= config["donateAmount"]:
                    updated = True
                await client.send_message(message.author, 'To donate, send an amount greater than $%s to: ```%s```Thank you :slight_smile:' % (config["donateAmount"], row[2]))
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
