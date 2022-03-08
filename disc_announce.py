from lib2to3.pgen2.parse import ParseError
from aiohttp import request
import discord
from discord import TextChannel
import requests 


import json
import logging 
import wordle
import sys 

   

class wordle_announcer(discord.Client):
    def __init__(self, targets, wordle_dict_path, *, loop=None, **options):
        super().__init__(loop=loop, **options)
        self.targets = targets
        self.lo = logging.getLogger("wordle_announcer")
        self.wordle = wordle.Wordle(wordle_dict_path)
        self.outstr = ""
        
    async def on_ready(self):
        self.lo.info("Bot loaded")
        self.wordle.solve()
        self.outstr = self.wordle.result_string(discord=True)
        await self.send_to_channels()
        await self.send_to_users()
        for guild in self.guilds:
            await self.get_thread(guild,self._connection)

        exit()



    async def send_to_users(self):
        targets = {} 
        
        for member in self.get_all_members():
            if member.id in config["userIDs"]:
                targets[member.id] = member
                
        for member_id in targets:
            await targets[member_id].send(self.outstr)

    async def send_to_channels(self):
        for channel in config["channels"]:
            channel_o = self.get_channel(channel)
            await channel_o.send(self.outstr)
        pass    
        
    async def get_thread(self,guild:discord.guild,client_connection_state) -> list:
        url = "https://discord.com/api/v10/guilds/{guild_id}/threads/active".format(guild_id=guild.id )
        
        headers = {
            'User-Agent': "DiscordBot (https://github.com/Ctri-The-Third/wordle)",
            'X-Ratelimit-Precision': 'millisecond',
        }
        headers['Authorization'] = 'Bot ' + config["token"]

        data = requests.get(url,headers=headers)
        content = {}
        try: 
            content = json.loads(data.content)
        except ParseError as e:
            self.lo.warning("Couldn't parse JSON from get_thread endpoint")
        
        if "threads" in content:
            for thread in content["threads"]:
                if "id" in thread and int(thread["id"]) in config["threads"]:
                    print("THIS IS A THREAD! :D")
                    thread["position"] = 0 
                    thread_o = TextChannel(guild=guild, state = self._connection, data= thread)
                    await thread_o.send(self.outstr)
        #self.http.get_channel(channel_id)
        
        #channel = TextChannel(guild=guild, state=client_connection_state, data=data)

    pass 

if __name__ == "__main__":
    

    intents = discord.Intents(
        messages=True, #need to read messages 
        emojis=True, 
        guild_messages=True, #need to read messages?
        members=True,  #need to get roles
        #presences=True,
        guilds=True #need to get roles
    )

    with open("disc_auth.json",'r') as json_file:
        config = json.load(json_file)
    if "logging" in config:
        try: 
            logging.basicConfig(level=config["logging"],format='%(asctime)s-%(process)d-%(name)s-%(levelname)s-%(message)s', handlers=[logging.StreamHandler(sys.stdout),logging.FileHandler("disc_announce.log")])
            logging.info("Set logging level to %s")
        except Exception as e :
            logging.error("couldn't set logging level - check auth.json for invalid values. \t %s" % (e))
    channels = config.get("targets")
    bot = wordle_announcer(channels, config.get("dictionary"),intents=intents )
    bot.run(config['token'])

