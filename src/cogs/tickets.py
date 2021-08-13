import json
import discord
import asyncio
from discord.errors import HTTPException

from discord.ext import commands
from discord.ext.commands.errors import CommandInvokeError


class Tickets(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.TICKET_CREATE_CHANNEL = '🎟・ticket-erstellen'
        self.TICKET_SUPPORT_CHANNEL = '📨・ticket・<name>'
        self.TICKET_SUPORT_NAME_BEGIN = '📨・ticket・'

    async def open_ticket(self, create_channel: discord.TextChannel, member: discord.Member, topic: str):
        for c in member.guild.text_channels:
            if str(member.id) in str(c.topic):
                return

        ticket_channel = await member.guild.create_text_channel(name=self.TICKET_SUPPORT_CHANNEL.replace('<name>', member.name), category=create_channel.category)
        await ticket_channel.edit(topic=f'Support Ticket | ID: {member.id}')
        await ticket_channel.set_permissions(member, connect=True, view_channel=True)
        await ticket_channel.set_permissions(discord.utils.get(member.guild.roles, name='@everyone'), connect=False, view_channel=False)

        msg = await ticket_channel.send(embed=discord.Embed(title=f'Support: {topic}', description='✅ Willkommen zum Ticket! Hier kann dir das Team weiterhelfen.\n> Um den Kanal zu schließen, sende `!ticketclose` oder reagiere mit :x:.', color=0xFF4400))

        await msg.add_reaction('❌')

        def check(reaction, user):
            return reaction.message == msg and not user.bot

        try:
            await self.client.wait_for('reaction_add', check=check)
        except asyncio.TimeoutError:
            return

        await self.close_ticket(channel=ticket_channel)

    async def close_ticket(self, channel):
        await channel.delete()

    @commands.has_permissions(manage_channels=True)
    @commands.command(help='🔒Erstellt ein für alle mal einen "Ticket-erstellen"-Kanal, benötigt entsprechende Berechtigungen.')
    async def ticketsetup(self, ctx, *args):
        args = ' '.join(args).split('\n')
        print(args)

        text = ''
        emoji = ''
        topics = {}
        emojis = ''

        for arg in args:
            emoji = arg.split(': ')[0]
            emojis += emoji
            topic = arg.split(': ')[1]

            topics[emoji] = topic
            text += f'{emoji}・**{topic}**\n'

        msg = await ctx.send(embed=discord.Embed(title='Support-Themen', description=f'> Wähle hier einfach aus, wobei du Hilfe brauchst!\n\n{text}', color=0xFF4400))

        for e in emojis:
            try:
                await msg.add_reaction(e)
            except HTTPException:
                pass

        json.dump(topics, open('config/ticket_topics.json', 'w',
                  encoding='utf8'), indent=4, ensure_ascii=False)

    @commands.command(help='🔒Löscht einen Ticket-Kanal, funktioniert **nur** in einem Ticketkanal')
    async def ticketclose(self, ctx):
        if ctx.channel.name.startswith(self.TICKET_SUPORT_NAME_BEGIN):
            await self.close_ticket(channel=ctx.channel)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        emoji = payload.emoji
        topics = json.loads(
            open('config/ticket_topics.json', encoding='utf8').read())
        # guild = await self.client.fetch_guild(payload.guild_id)
        channel = self.client.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        member = payload.member

        if (not member.bot) and channel.name == self.TICKET_CREATE_CHANNEL:
            try:
                await message.remove_reaction(payload.emoji, member)
                await self.open_ticket(channel, member=member, topic=topics[emoji.name])
            except KeyError:
                return


def setup(client):
    client.add_cog(Tickets(client))
