from telethon.sync import TelegramClient, events, Button
from telethon.tl.types import Channel, User, Updates
from telethon.tl.functions.channels import JoinChannelRequest, InviteToChannelRequest, LeaveChannelRequest
from credentials import Users
from telethon.errors import UserPrivacyRestrictedError, UserChannelsTooMuchError, UserNotMutualContactError
from telethon.errors.rpcerrorlist import FloodWaitError, PeerFloodError
from time import sleep
from telethon.tl.functions.users import GetFullUserRequest
from telethon.sessions import StringSession


class BackgroundBot:

    def __init__(self, channelUsername, IDChannelFollowers, event, loggedUser):
        self.me = None
        self.LoggedUser = Users[0]
        self.channelUsername = channelUsername
        self.IDChannelFollowers = IDChannelFollowers
        self.event = event
        self.client = None
        self.session = loggedUser
        self.count = 0

    async def startBot(self, event):

        print(f"BackgroundBot {self.LoggedUser['id']} Started {self.channelUsername} {self.IDChannelFollowers}")

        async with TelegramClient(StringSession(self.session), self.LoggedUser["API_ID"], self.LoggedUser["API_HASH"]) as client:

            print("OK")

            await self.event.respond("Session Started")
            self.me = await client.get_me()
            self.client = client
            print(self.IDChannelFollowers)
            requestChannel =  await self.channelRequestEnter(self.channelUsername, client)
            if requestChannel:
                requestChannel2 = await self.channelRequestEnter(self.IDChannelFollowers, client)
                if requestChannel2:
                    await self.handleInvites()

            await self.event.respond(f"Session Ended: {self.me.username}")
            await client.disconnect()

    async def stopBot(self):
        await self.client.disconnect()

    async def getID(self, id, client):
        ID = id
        if ID.isdigit():
            ID = int(id)
        entity = await client.get_entity(ID)
        return entity.id

    async def channelRequestEnter(self, channel, client) -> bool:
        try:
            ID = await self.getID(channel, client)
            async for i in client.iter_dialogs():
                if i.entity.id == ID:
                    return True
            await client(JoinChannelRequest(ID))
            async for i in client.iter_dialogs():
                if i.entity.id == ID:
                    return True
            await self.event.respond(f"Non Riesco ad entrare in {channel}, se persiste, aggiungere username: {self.me.username} manualmente nel gruppo")
            return False
        except:
            await self.event.respond(f"Non Riesco ad entrare in {channel}, se persiste, aggiungere username: {self.me.username} manualmente nel gruppo")
            return False

    async def getUsers(self):
        try:
            ID = await self.getID(self.IDChannelFollowers, self.client)
            Users = self.client.iter_participants(ID, aggressive=True)
            return Users
        except:
            self.event.respond("Impossibile prendere gli utenti")

    async def inviteUser(self, ID):
        try:
            result = await self.client(InviteToChannelRequest(
                channel=self.channelUsername,
                users=[ID]
            ))
            print(result)
            if isinstance(result, Updates):
                self.count = self.count+1
                CRED = '\033[91m'
                CEND = '\033[0m'
                print(CRED + "UPDATE" + CEND)
                #Add Users to File#
                with open("./IDsSended.txt", "a") as file:
                    file.write(f"{ID}\n")
        except UserPrivacyRestrictedError as e:
            print(e)
            print("Added")
            with open("./IDsSended.txt", "a") as file:
                file.write(f"{ID}\n")

        except UserChannelsTooMuchError as e:
            print(e)
            print("Added")
            with open("./IDsSended.txt", "a") as file:
                file.write(f"{ID}\n")

        except UserNotMutualContactError as e:
            print(e)
            print("Added")
            with open("./IDsSended.txt", "a") as file:
                file.write(f"{ID}\n")

        except PeerFloodError as e:
            self.count = 100

        except FloodWaitError as e:
            self.count = 100

        except Exception as e:
            print("OK")
            print(type(e))
            print(e)
            self.count = 100


    async def handleInvites(self):
        Users = await self.getUsers()
        async for user in Users:
            UserID = int(user.id)
            if self.count > 5:
                break
            with open("./IDsSended.txt", "r") as file:
                a:list = file.readlines()
                if f"{UserID}\n" in a:
                    print("Utente già invitato")
                else:
                    await self.inviteUser(UserID)
                    sleep(1.5)
