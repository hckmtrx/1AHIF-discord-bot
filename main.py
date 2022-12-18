import urllib.request, interactions, time, datetime

def GetEvents() -> list:
    content = urllib.request.urlopen("api url").read().decode()[1:]

    TWO_ZERO_TWO_TWO = [[], [], [], [], [], [], [], [], [], [], [], []]
    TWO_ZERO_TWO_THREE = [[], [], [], [], [], [], [], [], [], [], [], []]
    SORTED_DATE = []

    for i in range(len(content)):
        if content[i] == "{":
            content = content[i:]
            break

    def GetDateEnd(position: int) -> int:
        while True:
            if content[position] == '"':
                return position
            position += 1

    def GetDayOfDate(date: str) -> int:
        for i in range(1, 13):
            if int(date[5:7]) == i:
                return i - 1

    def SortDates(yearList: list, yearStr: str) -> None:
        for i in range(len(yearList)):
            lowest = []
            for a in range(len(yearList[i])):
                lowest.append(yearList[i][a][1])
            lowest.sort()

            while len(yearList[i]) != 0:
                b = 0
                while b < len(yearList[i]):
                    if yearList[i][b][1] == lowest[0]:
                        SORTED_DATE.append([yearList[i][b][0], str(yearList[i][b][1]) + "." + str(i + 1) + "." + yearStr])
                        yearList[i].pop(b)
                        lowest.clear()
                        for c in range(len(yearList[i])):
                            lowest.append(yearList[i][c][1])
                        lowest.sort()
                    b += 1

    i = 0
    while content.find("summary") != -1:
        nameIndex = content.find('"summary": "') + len('"summary": "')
        name = content[nameIndex : GetDateEnd(nameIndex)]

        dateIndex = content.find('"start": {\n    "date":') + len('"start": {\n    "date":') + 2
        date = content[dateIndex : GetDateEnd(dateIndex)]

        if datetime.datetime.strptime(date, "%Y-%m-%d") > datetime.datetime.strptime(datetime.datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d"):
            if date[:4] == "2022":
                TWO_ZERO_TWO_TWO[GetDayOfDate(date)].append([name, int(date[8:])])
            elif date[:4] == "2023":
                TWO_ZERO_TWO_THREE[GetDayOfDate(date)].append([name, int(date[8:])])
        i += 1
        content = content[GetDateEnd(dateIndex):]

    SortDates(TWO_ZERO_TWO_TWO, "2022")
    SortDates(TWO_ZERO_TWO_THREE, "2023")

    return SORTED_DATE

def GetThisWeeksKlassenordner() -> list:
    reader = open("class_list.txt", "r")
    classList = reader.readline().split("|")

    reader = open("last_klassenordner.txt", "r")
    lastKlassenordner = reader.readlines()

    for i in range(len(lastKlassenordner)):
        lastKlassenordner[i] = lastKlassenordner[i].rstrip("\n")

    if datetime.datetime.today().weekday() == 0 and lastKlassenordner[2] != datetime.datetime.today().strftime("%d.%m.%Y"):
        if lastKlassenordner[0] == "16":
            writer = open("last_klassenordner.txt", "w+")
            writer.write("0\n" + str(len(classList) - 1) + "\n" + datetime.datetime.today().strftime("%d.%m.%Y"))
            return classList[int(lastKlassenordner[0])]
        else:
            writer = open("last_klassenordner.txt", "w+")
            writer.write(str(int(lastKlassenordner[0]) + 1) + "\n" + str(int(lastKlassenordner[1]) - 1) + "\n" + datetime.datetime.today().strftime("%d.%m.%Y"))

    return [classList[int(lastKlassenordner[0])], classList[int(lastKlassenordner[1])]]

def GetTimeBasedOnLesson(event: str, date: list) -> int:
    lessons = [[8, 00], [8, 55], [10, 00], [10, 55], [11, 50], [12, 45], [13, 40], [14, 35]]
    monday = ["RW", "RW", "BO", "PH", "BO", "E", "CABS"]
    tuesday = ["M", "M", "E", "D", "D", "GGP", "SPK"]
    wednesday = ["RK", "RK", "STSW", "STSW", "WLC", "WLC", "GGP"]
    thursday = ["M", "M", "PRO", "PRO", "PRO", "PAUSE", "PRO", "PRO"]
    friday = ["PH", "PH", "BSPK", "BSPK", "D"]
    timeTable = [monday, tuesday, wednesday, thursday, friday]

    hours = 0; minutes = 0
    weekday = datetime.date(int(date[2]), int(date[1]), int(date[0])).weekday()
    for lesson in range(len(timeTable[weekday])):
        if event.startswith(timeTable[weekday][lesson]):
            hours = lessons[lesson][0]
            minutes = lessons[lesson][1]
            break
    
    return hours * 3600 + minutes * 60

bot = interactions.Client(token="bot token")

@bot.command(
    name="events",
    description="displays all upcoming events"
)
async def Events(ctx: interactions.CommandContext):
    SORTED_DATE = GetEvents()
    string = ">>> "
    for i in range(len(SORTED_DATE)):
        string += "~ _" + str(SORTED_DATE[i][0]) + "_\ttakes place <t:" + str(int(time.mktime(datetime.datetime.strptime(SORTED_DATE[i][1], "%d.%m.%Y").timetuple()) + GetTimeBasedOnLesson(SORTED_DATE[i][0], SORTED_DATE[i][1].split(".")))) + ":R>" + "\n"

    await ctx.send(string)

@bot.command(
    name="sical",
    description="displays the public ical url"
)
async def Sical(ctx: interactions.CommandContext):
    await ctx.send("for more info view the 1AHIF calendar: " + r"ical url")

@bot.command(
    name="klassenordner",
    description="displays this weeks klassenordner"
)
async def Klassenordner(ctx: interactions.CommandContext):
    await ctx.send("\n".join(GetThisWeeksKlassenordner()))

bot.start()