from telethon.sync import TelegramClient, events, Button
from telethon.tl.types import Channel, User, PeerChat, PeerChannel, DialogPeer
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import InputPeerChat
from telethon.errors import SessionPasswordNeededError,PhoneNumberFloodError
from credentials import Users, Numbers
import asyncio
import json
from time import sleep
from telethon.sessions import StringSession
from BackgroundBot import BackgroundBot

class BOT:

    def __init__(self):
        self.LoggedUser = Users[0]
        self.Getter = None
        #Flags
        self.flagStartBot = False
        self.flagDeleteVoip = False
        #Values
        self.channelUsername = ""
        self.channelFollowers = ""
        self.backgroundBot = None

        self.temp_client = None
        self.Number = None
        self.DeleteVoip = None
        with open("ArchivioVoips.json", "r") as file:
            js = json.load(file)
            self.ArchivedVoips = js

    async def start(self):
        async with TelegramClient("BOT", Users[0]["API_ID"], Users[0]["API_HASH"]) as client:
            print("...SmaverickBOT Started...")

            @client.on(events.NewMessage)
            async def handler(e):

               if self.Getter == 0:
                  await self.updateChannelUsername(e, client)

               elif self.Getter == 1:
                  await self.updateChannelFollowers(e, client)

               elif self.Getter == 5:
                  await self.updateVoip(e)

               elif self.Getter == 6:
                    await self.addVoip(e, client)

               elif self.Getter == 7:
                   await self.VoipCode(e, client)

               elif self.Getter == 8:
                   await self.VoipPassword(e, client)

               else:
                   await self.settings(e)


            @client.on(events.CallbackQuery())
            async def callbackQuery(e):
                try:
                    if e.data == b"channelUsername":
                        self.Getter = 0
                        await e.edit("Inserisci Username Canale (es: Fifa22)",buttons=[[Button.inline("❌ Annulla", "annulla"),]])

                    if e.data == b"channelFollowers":
                        self.Getter = 1
                        await e.edit("Inserisci Username Canale (es: Fifa22)",buttons=[[Button.inline("❌ Annulla", "annulla"), ]])

                    elif e.data == b"addvoip":
                        self.Getter = 6
                        await e.edit("Inserisci Numero VOIP",buttons=[[Button.inline("❌ Annulla", "annulla"),]])

                    elif e.data == b"listvoip":
                        voips = []
                        for voip in self.ArchivedVoips:
                            voips.append([Button.inline(voip, "")])
                        voips.append([Button.inline("❌ Indietro", "annulla")])
                        self.flagDeleteVoip = True
                        await e.edit("Lista VOIPS",buttons=voips)

                    elif e.data == b"deletevoip":
                        if self.DeleteVoip is not None:
                            if self.DeleteVoip in self.ArchivedVoips:
                                self.ArchivedVoips.pop(self.DeleteVoip, None)
                        self.DeleteVoip = None
                        self.flagDeleteVoip = False
                        await e.edit(
                            "Settings",
                            buttons=[
                                [Button.inline("Username Canale da Boostare: " + self.channelUsername,
                                               "channelUsername"), ],
                                [Button.inline("Username o ID Canale Followers: " + self.channelFollowers,
                                               "channelFollowers"), ],
                                [Button.inline("Aggiungi VOIP:", "addvoip"), ],
                                [Button.inline("Lista VOIPS:", "listvoip"), ],
                                [Button.inline("Start Bot", "start"), ],
                                [Button.inline("Stop Bot", "stop"), ],
                            ]
                        )

                    elif e.data == b"annulla":
                        self.flagDeleteVoip = False
                        self.Getter = None
                        self.DeleteVoip = None
                        await e.edit(
                            "Settings",
                            buttons=[
                                [Button.inline("Username Canale da Boostare: " + self.channelUsername,"channelUsername"),],
                                [Button.inline("Username o ID Canale Followers: " + self.channelFollowers,"channelFollowers"),],
                                [Button.inline("Aggiungi VOIP:", "addvoip"),],
                                [Button.inline("Lista VOIPS:", "listvoip"), ],
                                [Button.inline("Start Bot", "start"),],
                                [Button.inline("Stop Bot", "stop"),],
                            ]
                        )

                    elif e.data == b"stop":
                        await self.backgroundBot.stopBot()
                        self.flagStartBot = False
                        await e.respond("Bot Stopped.")

                    elif e.data == b"start":

                        if self.channelUsername == "":
                            await e.respond("Username Canale Vuoto")

                        if self.channelFollowers == "":
                            await e.respond("ID Canale Followers Vuoto")

                        if self.channelUsername != "" and self.channelFollowers != "" and not self.flagStartBot:
                            self.flagStartBot = True
                            for number in self.ArchivedVoips.keys():
                                self.backgroundBot = BackgroundBot(
                                    channelUsername=self.channelUsername,
                                    IDChannelFollowers=self.channelFollowers,
                                    event=e,
                                    loggedUser=self.ArchivedVoips[number],
                                )
                                await self.backgroundBot.startBot(e)
                            await e.respond("Bot Finished")
                            self.flagStartBot = False

                    elif self.flagDeleteVoip:
                        if e.data.decode('UTF-8') in self.ArchivedVoips:
                            self.DeleteVoip = e.data.decode("UTF-8")
                            await e.respond(f"Eliminare il voip: {e.data.decode('UTF-8')}?", buttons=[[Button.inline("Si", "deletevoip")],[Button.inline("No", "annulla")]])

                except Exception as e:
                    pass

            await client.run_until_disconnected()

    #Metodi
    async def settings(self, e):
        await e.respond(
            "Settings",
            buttons=[
                [Button.inline("Nome Canale Boost: " + self.channelUsername, "channelUsername"),],
                [Button.inline("Nome Canale Followers: " + self.channelFollowers, "channelFollowers"),],
                [Button.inline("Aggiungi VOIP:", "addvoip"),],
                [Button.inline("Lista VOIPS:", "listvoip"), ],
                [Button.inline("Start Bot", "start"),],
                [Button.inline("Stop Bot", "stop"),],
            ]
        )

    async def updateChannelUsername(self, e, client):
        try:
            entity = await client.get_entity(e.text)
            if isinstance(entity, Channel):
                self.channelUsername = e.text
            else:
                await e.respond("Username Channel Non Valido")
        except:
            await e.respond("Username Channel Non Valido")
        finally:
            self.Getter = None

    async def updateChannelFollowers(self, e, client):
        try:
            entity = await client.get_entity(e.text)
            if isinstance(entity, Channel):
                self.channelFollowers = e.text
                self.Getter = None
            else:
                await e.respond("Username Channel Non Valido")
        except:
            await e.respond("Username Channel Non Valido")
        finally:
            self.Getter = None

    async def addVoip(self, e, client):
        try:
            self.temp_client = TelegramClient(StringSession(), Users[0]["API_ID"], Users[0]["API_HASH"])
            await self.temp_client.connect()
            await self.temp_client.send_code_request(phone=e.text, force_sms=False)
            self.Number = e.text
            self.Getter = 7
            await e.respond("Inserisci codice di accesso", buttons=[[Button.inline("❌Annulla", "annulla"), ]])

        except PhoneNumberFloodError:
            await e.respond("Numero in floodwait, aspetta prima di poterlo riutilizzare")
            self.Getter = None

        except Exception as exception:
            print(exception)
            await e.respond("Errore, riprova tra un po o cambia numero")
            self.Getter = None

    async def VoipCode(self, e, client):
        try:
            await self.temp_client.sign_in(phone=self.Number, code=e.text)
            self.ArchivedVoips[self.Number] = StringSession.save(self.temp_client.session)
            with open("ArchivioVoips.json", "w") as file:
                json.dump(self.ArchivedVoips, file)
            await e.respond("Voip Aggiunto")
            self.Getter = None
            self.Number = None
        except SessionPasswordNeededError:
            self.Getter = 8
            await e.respond("Inserisci la Password")
        except Exception as exception:
            self.Getter = None

    async def VoipPassword(self, e, client):
        try:
            await self.temp_client.sign_in(phone=self.Number, password=e.text)
            self.ArchivedVoips[self.Number] = StringSession.save(self.temp_client.session)
            with open("ArchivioVoips.json", "w") as file:
                json.dump(self.ArchivedVoips, file)
            self.Number = None
            self.Getter = None
            await e.respond("Voip Aggiunto")

        except Exception as exception:
            await e.respond("Errore")
            self.Getter = None

bot = BOT()
asyncio.run(bot.start())
