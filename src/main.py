import os
import dotenv
import socket
import discord

from discord.ext import commands

dotenv.load_dotenv() # initialize virtual enviroment

COLOR = discord.Color(0xff6500) # primary color for embeds
TESTING_MODE = socket.gethostname() in ['RTX3090', 'uwuntu'] # testing systems
PREFIX = '!' # command prefix

client = commands.Bot(command_prefix=commands.when_mentioned_or(PREFIX), help_command=None) # create bot, help_command is none because it's a custom one

@client.event
async def on_ready():
    print('ONLINE as', client.user)
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='programmiert von onlix#1662'))

@client.event
async def on_command_error(ctx, error):
    error_messages = {
        commands.ExtensionError: 'Es gab ein Problem in einer Erweiterung ("cog").',
        commands.CheckFailure: 'Es gab ein Problem mit der Überprüfung, ob etwas ausgeführt werden soll.',
        commands.UserInputError: 'Überprüfe bitte deine Eingabe.',
        commands.CommandNotFound: f'Befehl nicht gefunden. Benutze **`{PREFIX}help`** für eine Befehlsliste.',
        # the f-string generates the help-command for the command
        commands.MissingRequiredArgument: f'Du hast ein Befehlsargument vergessen, benutze **`{PREFIX}help {ctx.message.content.replace(PREFIX, "").split()[0]}`** für Hilfe.',
        # the f-string generates the help-command for the command
        commands.TooManyArguments: f'Du hast zu viele Argumente eingegeben, benutze **`{PREFIX}help {ctx.message.content.replace(PREFIX, "").split()[0]}`** für Hilfe.',
        commands.Cooldown: 'Bitte warte, du kannst diesen Befehl erst später ausführen.',
        # commands.MessageNotFound: 'This message could not be found.',
        # commands.ChannelNotFound: 'This channel could not be found.',
        commands.NoPrivateMessage: 'Dies Funktioniert nicht in DM-Kanälen.',
        commands.MissingPermissions: 'Du brauchst leider folgende Berechtigung(en), um das zu tun:',
        commands.BotMissingPermissions: 'Ich brauche folgende Berechtigung(en), um das zu tun:',
        # the f-string generates the help-command for the command
        commands.BadArgument: f'Es gab ein Problem mit dem Konvertieren der Argumente, benutze den folgenden Befehl für Hilfe: **`{PREFIX}help {ctx.message.content.replace(PREFIX, "").split()[0]}`**',
    }

    error_msg = 'Unbekannter Fehler.'

    # create the error message using the dict above
    for e in error_messages.keys():
        if isinstance(error, e):
            error_msg = error_messages[e]

    # other errors:
    # - too long
    if 'Invalid Form Body' in str(error): error_msg = 'Ich kann leider nicht die Nachricht senden, weil sie zu lang gewesen wäre.'

    # - bug
    if 'Command raised an exception' in str(error): error_msg = 'Huch, es gab ein Problem mit dem Code.'

    # add detailed info
    if isinstance(error, commands.MissingPermissions) or isinstance(error, commands.BotMissingPermissions):
        error_msg += f'\n**`{", ".join(error.missing_perms)}`**\n'

    # add full error description formatted as a code text
    error_msg += '\n\n**Konsole:**\n```\n' + str(error) + '\n```'

    # create a cool embed
    embed = discord.Embed(
        title='Command Error',
        description=error_msg,
        color=0xFF0000
    )

    # send it
    await ctx.send(embed=embed)
    if TESTING_MODE or error_msg == 'Unbekannter Fehler.': raise error  # if this is a testing system, show the full error in the console

@client.command(aliases=['command', 'commands', 'help'], help='📃Befehlsinformation.', usage='(<command name>)')
async def commandinfo(ctx, name=None):
  if name:
    for c in client.commands:
      if name.lower() == c.name or name.lower() in list(c.aliases):
        text = f'''
        **Info:** {c.help if c.help else ' - '}
        **Benutzung:** {c.usage if c.usage else ' - '}
        **Aliasse:** {', '.join(c.aliases) if c.aliases else ' - '}
        '''
        embed = discord.Embed(title='Befehl ' + c.name, color=COLOR, description=text)
        await ctx.send(embed=embed)

        return

    embed = discord.Embed(title='Befehl nicht gefunden', color=COLOR, description='Benutze den help-Befehl für eine Liste mit allen Befehlen.')
    await ctx.send(embed=embed)
   
  else:
    def sortkey(x):
      return x.name
    
    categories = {'🚨': 'Hauptsystem', '📃': 'Info', '🔧': 'Tools', '🔒': 'Moderatoren-Tools', '🔩': 'Sonstige'}
    
    text = ''
    for category in categories.keys():
      text += f'\n{category} **{categories[category]}**\n'
      for command in sorted(client.commands, key=sortkey):
        if command.help.startswith(category):
          if command.aliases:
            text += f'{command.name} *({"/".join(command.aliases)})*\n'
          else:
            text += f'{command.name}\n'
          continue


    embed = discord.Embed(title='Befehle', color=COLOR, description=text)
    embed.set_footer(text=':)')
    await ctx.send(embed=embed)

for filename in os.listdir(os.getcwd() + '/src/cogs/'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

client.run(os.getenv('DISCORD_TOKEN')) # run bot with the token set in the .env file