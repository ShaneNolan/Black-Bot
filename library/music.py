#Music Player. (Alpha Version 0.2)
#WIP Features: Skip, Pause, Resume.

import discord
import queue
import youtube_dl

if not discord.opus.is_loaded():
    discord.opus.load_opus()

#Dictionary: ServerID | Plalist Object
serverPlaylists = {}

async def getPlaylist(message):
    if message.server.id not in serverPlaylists:
        serverPlaylists[message.server.id] = Playlist()

    return serverPlaylists[message.server.id]

class Playlist:
    def __init__(self):
        self.songList = queue.Queue()
        self.currentSong = None

    def nextSong(self):
        if not self.songList.empty():
            self.currentSong = self.songList.get()
            self.currentSong.start()

    async def addSong(self, player):
        self.songList.put(player)

    async def isPlaying(self):
        if self.currentSong != None:
            return True
        return False

class MusicPlayer:
    def __init__(self, client, message):
        self.channel = None
        self.player = None
        self.serverID = message.server.id

    async def play(self, client, message):
        currentPlaylist = await getPlaylist(message)
        opts = {'extractaudio' : True,
                'format' : 'bestaudio/best',
                'audioformat' : 'mp3',
                'default_search': 'auto',
                'nocheckcertificate': True,
                'ignoreerrors': True,
                'no_warnings': True,
                'quiet': True,
                'socket_timeout': 3,
                'cachedir': 'cache/'}

        if not client.is_voice_connected(message.server):
            self.channel = await client.join_voice_channel(message.author.voice_channel)
        else:
            self.channel = client.voice_client_in(message.server)

        try:
            self.player = await self.channel.create_ytdl_player(message.content[5:], ytdl_options=opts, after=currentPlaylist.nextSong())
        except:
            await client.send_message(message.channel, "Something went wrong. :(")
            return

        await client.send_message(message.channel, "Song added successfully. :)")
        await currentPlaylist.addSong(self.player)

        if not await currentPlaylist.isPlaying():
            currentPlaylist.nextSong()
