#https://github.com/Rapptz/discord.py/blob/async/examples/playlist.py

import asyncio
import discord

if not discord.opus.is_loaded():
    discord.opus.load_opus('opus')

class VoiceEntry:
    def __init__(self, message, player):
        self.requester = message.author
        self.channel = message.channel
        self.player = player

    def __str__(self):
        fmt = '*{0.title}* requested by {1.display_name}'
        duration = self.player.duration
        if duration:
            fmt = fmt + ' [Length: {0[0]}m {0[1]}s]'.format(divmod(duration, 60))
        return fmt.format(self.player, self.requester)

class VoiceState:
    def __init__(self, bot):
        self.current = None
        self.voice = None
        self.bot = bot
        self.play_next_song = asyncio.Event()
        self.songs = asyncio.Queue()
        self.skip_votes = set()
        self.audio_player = self.bot.loop.create_task(self.audio_player_task())

    def is_playing(self):
        if self.voice is None or self.current is None:
            return False

        player = self.current.player
        return not player.is_done()

    @property
    def player(self):
        return self.current.player

    def skip(self):
        self.skip_votes.clear()
        if self.is_playing():
            self.player.stop()

    def toggle_next(self):
        self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    async def audio_player_task(self):
        while True:
            self.play_next_song.clear()
            self.current = await self.songs.get()
            await self.bot.send_message(self.current.channel, '*Now playing*: ' + str(self.current))
            self.current.player.start()
            await self.play_next_song.wait()

class Music:
    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, message):
        state = self.voice_states.get(message.server.id)
        if state is None:
            state = VoiceState(self.bot)
            self.voice_states[message.server.id] = state

        return state

    def __unload(self):
        for state in self.voice_states.values():
            try:
                state.audio_player.cancel()
                if state.voice:
                    self.bot.loop.create_task(state.voice.disconnect())
            except:
                pass

    async def summon(self, message):
        summoned_channel = message.author.voice_channel
        if summoned_channel is None:
            await self.bot.send_message(message.channel, 'You are not in a voice channel.')
            return False

        state = self.get_voice_state(message)
        if state.voice is None:
            state.voice = await self.bot.join_voice_channel(summoned_channel)
        else:
            await state.voice.move_to(summoned_channel)

        return True

    async def play(self, message, *, song : str):
        state = self.get_voice_state(message)
        opts = {
            'default_search': 'auto',
            'extractaudio' : True,
            'format' : 'bestaudio/best',
            'audioformat' : 'mp3',
            'ignoreerrors': True,
            'no_warnings': True,
            'quiet': True,
        }

        if state.voice is None:
            success = await self.summon(message)
            if not success:
                return

        try:
            player = await state.voice.create_ytdl_player(song[5:], ytdl_options=opts, after=state.toggle_next)
        except Exception as e:
            fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
            await self.bot.send_message(message.channel, fmt.format(type(e).__name__, e))
        else:
            entry = VoiceEntry(message, player)
            await self.bot.send_message(message.channel, '*Enqueued*: ' + str(entry))
            await state.songs.put(entry)

    async def pause(self, message):
        state = self.get_voice_state(message)
        if state.is_playing():
            player = state.player
            player.pause()

    async def resume(self, message):
        state = self.get_voice_state(message)
        if state.is_playing():
            player = state.player
            player.resume()

    async def stop(self, message):
        server = message.server
        state = self.get_voice_state(message)

        if state.is_playing():
            player = state.player
            player.stop()

        try:
            state.audio_player.cancel()
            del self.voice_states[message.server.id]
            await state.voice.disconnect()
        except:
            pass

    async def skip(self, message):
        state = self.get_voice_state(message)
        if not state.is_playing():
            await self.bot.send_message(message.channel, 'Not playing any music right now...')
            return

        voter = message.author
        if voter == state.current.requester:
            await self.bot.send_message(message.channel, 'Requester requested skipping song...')
            state.skip()
        elif voter.id not in state.skip_votes:
            state.skip_votes.add(voter.id)
            total_votes = len(state.skip_votes)
            if total_votes >= 3:
                await self.bot.send_message(message.channel, 'Skip vote passed, skipping song...')
                state.skip()
            else:
                await self.bot.send_message(message.channel, 'Skip vote added, currently at [{}/3]'.format(total_votes))
        else:
            await self.bot.send_message(message.channel, 'You have already voted to skip this song.')

    async def playing(self, message):
        state = self.get_voice_state(message)
        if state.current is None:
            await self.bot.send_message(message.channel, 'Not playing anything.')
        else:
            skip_count = len(state.skip_votes)
            await self.bot.send_message(message.channel, 'Now playing {} [skips: {}/3]'.format(state.current, skip_count))
