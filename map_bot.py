import discord
import urllib.request
from discord.ext import commands
from PIL import Image


class Country:
    def __init__(self, name, color=(0,0,0), isVassal = False):
        self.name = name
        self.file_name = ''
        self.color = color
        self.vassals = []
        self.isVassal = isVassal
        self.overlord = None
    def addVassal(self, vassal):
        if vassal is not None:
            self.vassals.append(vassal)
            vassal.overlord = self
            vassal.isVassal = True
    def getFileName(self):
        if self.file_name == '':
            weirdoDict = listWeirdos()
            if self.name in weirdoDict:
                self.file_name = weirdoDict[self.name]
            else:
                self.file_name = self.name
    def findColor(self):
        self.getFileName()
        countryFile = open(createDirectory()+self.file_name+'.txt')
        for n in range(5):
            line = countryFile.readline()
        line = line.split('{'); line = line[1].split('}')
        line = line[0].strip(); line = line.split()
        self.color = (int(line[0]), int(line[1]), int(line[2]))

def collectCountries():
    countryList = []
    overlord = None
    with open('player_country_list.txt', 'r') as countryFile:
        for line in countryFile:
            line = line.strip()
            if '-' not in line:
                newCountry = Country(line)
                overlord = newCountry
                countryList.append(newCountry)
            elif '-' in line:
                name = line[1:]
                newVassal = Country(name)
                overlord.addVassal(newVassal)
                countryList.append(newVassal)
    for country in countryList:
        country.findColor()
    ocean = Country('ocean', (68, 107, 163))
    uncolonized = Country('uncolonized', (150, 150, 150))
    wasteland = Country('wasteland', (94, 94, 94))
    for feature in [ocean, uncolonized, wasteland]:
        countryList.append(feature)
    return countryList

def listWeirdos():
    weirdoDict = {'game_name':'file_name'}
    with open('weird_names.txt', 'r') as weirdoFile:
        for line in weirdoFile:
            equivalency = line.split(' = ')
            equivalency[1] = equivalency[1].strip()
            weirdoDict[equivalency[0]] = equivalency[1]
    return weirdoDict

def createDirectory():
    file = open('eu4_directory.txt','r')
    eu4Directory = file.readline()
    file.close()
    totalDirectory  = eu4Directory+'\common\countries\\'
    return totalDirectory

def getColorList(countryList):
    colorDict = {}
    for country in countryList:
        if country.isVassal:
            colorDict[country.color] = country.overlord.color
        else:
            colorDict[country.color] = country.color
    return colorDict

def changeColors(inputImage):
    im = Image.open(inputImage)
    colorDict = getColorList(collectCountries())
    newImData = []
    for color in im.getdata():
        if color in colorDict:
            newImData.append(colorDict[color])
        else:
            newImData.append((150,150,150))
    newIm = Image.new(im.mode,im.size)
    newIm.putdata(newImData)
    return newIm


# Defines Bot, Bot prefix, and bot description
bot = commands.Bot(command_prefix = '%', description = 'Hopefully this works!')

@bot.command(pass_context = True)
async def file(ctx):
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    URL = ctx.message.attachments[0]['url']
    req = urllib.request.Request(URL, headers={'User-Agent': user_agent})
    with urllib.request.urlopen(req) as url:
        with open('player_country_list.txt', 'wb') as f:
            f.write(url.read())

@bot.command(pass_context = True)
async def list(ctx):
    print(ctx.message)

@bot.command()
async def getlist():
    countryList = collectCountries()
    message = ''
    for country in countryList:
        if country.name not in ['ocean','uncolonized','wasteland']:
            name = country.name
            if country.isVassal:
                name = '-'+country.name
            message = message + (name) +'\n'
    await bot.say(message)

@bot.command(pass_context = True)
async def create(ctx):
    inputImage = 'original.png'
    outputImage = 'final.png'
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    if len(ctx.message.attachments) > 0:
        await bot.say('Processing')
        URL = ctx.message.attachments[0]['url']
        req = urllib.request.Request(URL, headers={'User-Agent': user_agent})
        with urllib.request.urlopen(req) as url:
            with open(inputImage, 'wb') as f:
                f.write(url.read())
        changeColors(inputImage).save(outputImage)
        await bot.send_file(bot.get_channel("336262010033405952"), open(outputImage, 'rb'))
        await bot.say('Done')
    else:
        await bot.say('Invalid command entry, upload an image and type "%create" in the "add a comment" part')


bot.run()
