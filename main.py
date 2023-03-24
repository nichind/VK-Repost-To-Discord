import vk_api, asyncio, json, discord, time, aiohttp, io, os, requests
import config as cfg
from discord.ext import commands, tasks
from discord import app_commands

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
vk_session = vk_api.VkApi(token=cfg.token)
vk = vk_session.get_api()

tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name='Репосчу аниме картиночки...'))

    print('''
     __      ___  _______                      _   ____        _   
     \ \    / / |/ /  __ \                    | | |  _ \      | |  
      \ \  / /| ' /| |__) |___ _ __   ___  ___| |_| |_) | ___ | |_ 
       \ \/ / |  < |  _  // _ \ '_ \ / _ \/ __| __|  _ < / _ \| __|
        \  /  | . \| | \ \  __/ |_) | (_) \__ \ |_| |_) | (_) | |_ 
         \/   |_|\_\_|  \_\___| .__/ \___/|___/\__|____/ \___/ \__|
                              | |                                  
                              |_|                                      
        ''')

    await tree.sync()
    requests.patch(url='https://discord.com/api/v9/users/@me', headers= {"authorization": cfg.dsbot_token}, json= {"bio": "вау!"})
    while True:
        for domain in cfg.domain:
            await getposts(domain)
        await client.change_presence(activity=discord.Game(name=f'Репосчу аниме картиночки... Всего картинок: {getcount()}'))
        await asyncio.sleep(30)



@tree.command(name='subscribe')
async def sub(interaction: discord.Interaction):
    '''Подписаться на канал с аниме девочками'''
    role = interaction.guild.get_role(cfg.roleid)
    await interaction.user.add_roles(role)
    await interaction.response.send_message(f'Вы подписались на VK Repost')

@tree.command(name='unsubscribe')
async def sub(interaction: discord.Interaction):
    '''Отписаться от канала с аниме девочками...'''
    role = interaction.guild.get_role(cfg.roleid)
    await interaction.user.remove_roles(role)
    await interaction.response.send_message(f'Вы отписались от VK Repost')


def checkpostid(groupdomain, id):
    try:
        with open('vkrepost/post.json', 'r') as f:
            post = json.load(f)
        return post[f'{groupdomain}'] != id
    except:
        with open('vkrepost/post.json', 'r') as f:
            post = json.load(f)
        post[str(groupdomain)] = '1'
        with open('vkrepost/post.json', 'w') as f:
            json.dump(post, f)
        return True

def counter(len):
    try:
        with open('vkrepost/post.json', 'r') as f:
            post = json.load(f)
        post[str('total')] = str(int(post[f'total']) + int(len))
        with open('vkrepost/post.json', 'w') as f:
            json.dump(post, f)
        return int(post[str('total')])
    except:
        with open('vkrepost/post.json', 'r') as f:
            post = json.load(f)
        post[str('total')] = '1'
        with open('vkrepost/post.json', 'w') as f:
            json.dump(post, f)
        return 1

def getcount():
    with open('vkrepost/post.json', 'r') as f:
        post = json.load(f)
    return post[f'total']

async def getposts(groupdomain):
    try:
        post = vk.wall.get(domain=groupdomain, offset=1)['items'][0]
        ds_channel = client.get_guild(cfg.dsserverid).get_channel(cfg.dschannelid)

        embed = discord.Embed(title=' ', description=' ')
        embeds = []
        files = []
        embeds.append(discord.Embed(title=f"Новый пост в {groupdomain}", description=f'https://vk.com/{groupdomain}/'))
        if checkpostid(groupdomain, post['id']) == True:
            with open('vkrepost/post.json', 'r') as f:
                jso = json.load(f)
            jso[f'{groupdomain}'] = post['id']
            with open('vkrepost/post.json', 'w') as f:
                json.dump(jso, f)

            for image in post['attachments']:
                maxheight = 1
                image_url = 'link'
                for img in image['photo']['sizes']:
                    if img['height'] > maxheight:
                        maxheight = img['height']
                        image_url = img['url']

                async with aiohttp.ClientSession() as session:
                    async with session.get(image_url) as resp:
                        img = await resp.read()
                        with io.BytesIO(img) as file:
                            files.append(discord.File(file, 'vkrepost by nichind#7644.png'))
                            embeds.append(discord.Embed(title=' ', description=' ').set_image(url=image_url))
            counter(len(post['attachments']))
            todelete = await ds_channel.send(f'<@&{cfg.roleid}>')
            await todelete.delete(delay=5)
            await ds_channel.send(embeds=embeds)
    except:
        print('Something went wrong.')

if __name__ == '__main__':
    client.run(cfg.dsbot_token)