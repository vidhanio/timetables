from datetime import time
import requests, io, discord, json, re, pprint, copy
from discord.ext import commands
from os.path import join, dirname
from settings import *
from pdfminer.high_level import extract_pages, extract_text
from pdfminer.layout import LTTextBoxHorizontal

# Validate PDF as courses PDF.
def validate_pdf(pdf_url: str):

    # Load PDF from URL.
    response = requests.get(pdf_url)
    pdf = io.BytesIO(response.content)

    # Check if "Student Timetables" is somewhere in the document.
    if "Student Timetables" not in extract_text(pdf):
        return False
    else:
        return True


# Validate element in PDF, remove useless elements.
def validate_element(element: str):

    invalid_elements = [
        "Term",
        "Week",
        "Semester",
        "1",
        "2",
        "AM",
        "PM",
        "Class",
        "N/A",
        "HF1:",
        "2021/2022",
    ]

    if element in invalid_elements:
        return False

    else:
        return True


# Generate info from PDF.
def generate_student_info(pdf_url: str):

    # Load PDF from URL
    response = requests.get(pdf_url)
    pdf = io.BytesIO(response.content)

    # Look for actual course table element along with the name element.
    name_found = False
    for page_layout in extract_pages(pdf):
        for element in page_layout:
            if (
                isinstance(element, LTTextBoxHorizontal)
                and "Semester 1" in element.get_text()
            ):
                courses_element = element.get_text()

            elif name_found == False:
                name = {
                    "first_name": element.get_text().split(", ")[1].strip(),
                    "last_name": element.get_text().split(", ")[0].strip(),
                }

                name_found = True

    # Filter list to remove useless text.
    courses_list = list(filter(validate_element, courses_element.split()))
    courses_list = list(
        filter(
            lambda a: not re.compile("^[A-Z]$").match(a),
            courses_list,
        )
    )

    courses_list = [
        words.rstrip(",")
        for segments in courses_list
        for words in segments.split(",")
        if words
    ]

    student_number = courses_list.pop(0)

    # Find course codes by matching regex pattern.
    course_codes = list(
        filter(
            re.compile("^[A-Z][A-Z][A-Z][0-9][A-Z][A-Z0-9]-[A-Z]$").match,
            courses_list,
        )
    )

    # Find first initials by matching regex pattern.

    # Find rooms by matching by matching regex pattern.
    rooms = list(
        filter(
            re.compile("^([0-9][0-9][0-9]|GYM)$").match,
            courses_list,
        )
    )

    # Last names are tricky because they do not match a pattern.
    # Instead, we just subtract all the already found information, and we are left with the last names.
    names = [item for item in courses_list if item not in course_codes + rooms]

    # If there are any study periods, add that information to all of the lists.
    study_indexes = [i for i, x in enumerate(names) if x == "STUDY"]

    for i in study_indexes:
        course_codes.insert(i, "STUDY")
        names[i] = "Study"
        rooms.insert(i, 0)

    # This represents the order of the courses in relation to how they were parsed.
    order = [0, 4, 1, 5, 2, 6, 3, 7, 8, 12, 9, 13, 10, 14, 11, 15]

    # Order elements in correct order defined above.
    courses_dict = {
        "course_codes": [course_codes[i] for i in order],
        "names": [names[i] for i in order],
        "rooms": [rooms[i] for i in order],
    }

    # Initialize student info dictionary.
    student_info = {
        "name": name,
        "student_number": student_number,
        "courses": [
            [
                [
                    [
                        {
                            "course_code": "",
                            "teacher": "",
                            "room": 0,
                        },
                        {
                            "course_code": "",
                            "teacher": "",
                            "room": 0,
                        },
                    ],
                    [
                        {
                            "course_code": "",
                            "teacher": "",
                            "room": 0,
                        },
                        {
                            "course_code": "",
                            "teacher": "",
                            "room": 0,
                        },
                    ],
                ],
                [
                    [
                        {
                            "course_code": "",
                            "teacher": "",
                            "room": 0,
                        },
                        {
                            "course_code": "",
                            "teacher": "",
                            "room": 0,
                        },
                    ],
                    [
                        {
                            "course_code": "",
                            "teacher": "",
                            "room": 0,
                        },
                        {
                            "course_code": "",
                            "teacher": "",
                            "room": 0,
                        },
                    ],
                ],
            ],
            [
                [
                    [
                        {
                            "course_code": "",
                            "teacher": "",
                            "room": 0,
                        },
                        {
                            "course_code": "",
                            "teacher": "",
                            "room": 0,
                        },
                    ],
                    [
                        {
                            "course_code": "",
                            "teacher": "",
                            "room": 0,
                        },
                        {
                            "course_code": "",
                            "teacher": "",
                            "room": 0,
                        },
                    ],
                ],
                [
                    [
                        {
                            "course_code": "",
                            "teacher": "",
                            "room": 0,
                        },
                        {
                            "course_code": "",
                            "teacher": "",
                            "room": 0,
                        },
                    ],
                    [
                        {
                            "course_code": "",
                            "teacher": "",
                            "room": 0,
                        },
                        {
                            "course_code": "",
                            "teacher": "",
                            "room": 0,
                        },
                    ],
                ],
            ],
        ],
    }

    # Iterate through each course in the lists, and add that info to the main dictionary.
    counter = 0
    for semester in range(2):
        for term in range(2):
            for week in range(2):
                for course in range(2):
                    student_info["courses"][semester][term][week][course][
                        "course_code"
                    ] = courses_dict["course_codes"][counter]
                    student_info["courses"][semester][term][week][course][
                        "teacher"
                    ] = courses_dict["names"][counter]
                    student_info["courses"][semester][term][week][course][
                        "room"
                    ] = courses_dict["rooms"][counter]

                    counter += 1

    return student_info


def generate_shared_courses_embed(shared_courses: dict):
    shared_courses_embed = discord.Embed(
        title="Courses shared with {}".format(shared_courses[0]["name"]["first_name"]),
        description="You share {}/16 courses.".format(len(shared_courses)),
    )

    sem_lists = []

    for semester in range(2):
        sem_lists.append([])
        for term in range(2):
            sem_lists[semester].append("__**Term {}**__".format(term + 1))
            for week in range(2):
                sem_lists[semester].append("**Week {}**".format(week + 1))
                courses_added = 0
                for course in shared_courses:
                    if [course["semester"], course["term"], course["week"],] == [
                        semester,
                        term,
                        week,
                    ]:
                        sem_lists[semester].append(
                            "{} ({})".format(
                                course["course"]["course_code"],
                                course["course"]["teacher"],
                            )
                        )
                        courses_added += 1
                sem_lists[semester].extend([""] * (2 - courses_added))

    shared_courses_embed.set_author(
        name=shared_courses[0]["user"].name,
        icon_url=shared_courses[0]["user"].avatar_url,
    )
    shared_courses_embed.add_field(name="Semester 1", value="\n".join(sem_lists[0]))
    shared_courses_embed.add_field(name="Semester 2", value="\n".join(sem_lists[1]))

    shared_courses_embed.set_footer(
        text="Made with ❤️ by Vidhan",
        icon_url="https://avatars.githubusercontent.com/u/41439633?",
    )

    return shared_courses_embed


def generate_shared_students_embed(user: dict):
    courses_embed = discord.Embed(
        title="{}'s Classes".format(user["name"]["first_name"]),
    )

    for semester in range(2):
        for term in range(2):
            for week in range(2):
                for course in range(2):
                    if user["courses"][semester][term][week][course]["shared_with"]:
                        users = "\n".join(
                            [
                                "{} ({})".format(
                                    user_.mention,
                                    timetables["users"][str(user_.id)]["name"][
                                        "first_name"
                                    ],
                                )
                                for user_ in user["courses"][semester][term][week][
                                    course
                                ]["shared_with"]
                            ]
                        )
                    else:
                        users = "\u200D"
                    courses_embed.add_field(
                        name="{} ({})".format(
                            user["courses"][semester][term][week][course][
                                "course_code"
                            ],
                            user["courses"][semester][term][week][course]["teacher"],
                        ),
                        value=users,
                    )
    courses_embed.set_author(
        name=user["user"].name,
        icon_url=user["user"].avatar_url,
    )
    courses_embed.set_footer(
        text="Made with ❤️ by Vidhan",
        icon_url="https://avatars.githubusercontent.com/u/41439633?",
    )
    return courses_embed


def generate_courses_embed(user: dict):

    courses_embed = discord.Embed(
        title="{}'s Courses".format(user["name"]["first_name"]),
    )

    sem_lists = []

    for semester in range(2):
        sem_lists.append([])
        for term in range(2):
            sem_lists[semester].append("__**Term {}**__".format(term + 1))
            for week in range(2):
                sem_lists[semester].append("**Week {}**".format(week + 1))
                for course in range(2):
                    sem_lists[semester].append(
                        "{} ({})".format(
                            user["courses"][semester][term][week][course][
                                "course_code"
                            ],
                            user["courses"][semester][term][week][course]["teacher"],
                        )
                    )

    courses_embed.set_author(
        name=user["user"].name,
        icon_url=user["user"].avatar_url,
    )
    courses_embed.add_field(name="Semester 1", value="\n".join(sem_lists[0]))
    courses_embed.add_field(name="Semester 2", value="\n".join(sem_lists[1]))

    courses_embed.set_footer(
        text="Made with ❤️ by Vidhan",
        icon_url="https://avatars.githubusercontent.com/u/41439633?",
    )

    return courses_embed


def error_embed(text: str):
    error = discord.Embed(title="Error! :confused:", description=text, colour=0xF7768E)
    return error


def success_embed(text: str):
    success = discord.Embed(title="Success! :smile:", description=text, colour=0x73DACA)
    return success


# Allow bot to have all intents.
intents = discord.Intents.all()

# Set prefix.
bot = commands.Bot(command_prefix="tt.", intents=intents)

# Read from timetables.json to initialize info.
with open(join(dirname(__file__), "timetables.json"), "r") as timetables_json:
    timetables = json.load(timetables_json)


# tt.set: Set your timetable by uploading it in the same message as the command.
@bot.command(name="set")
async def _set(ctx, user: discord.User = None):

    # Check if a user was passed.
    if user:
        if ctx.author.id != 277507281652940800:
            await ctx.send(embed=error_embed("You aren't Vidhan, you can't do that."))
            return
    else:
        user = ctx.author

    # Check if message has attachments.
    if ctx.message.attachments:
        timetable_url = str(ctx.message.attachments[0])

        # Check if message has .pdf file extension.
        if timetable_url.lower()[-4:] != ".pdf":
            await ctx.send(embed=error_embed("Attachment is not a PDF."))
            return

        # Check if pdf is valid.
        elif not validate_pdf(timetable_url):
            await ctx.send(embed=error_embed("PDF is not valid."))
            return

        # Generate student info and store it in dictionary, as well as writing it to the timetables.json.
        else:
            timetables["users"][str(user.id)] = generate_student_info(timetable_url)

            with open(
                join(dirname(__file__), "timetables.json"), "w"
            ) as timetables_json:
                json.dump(timetables, timetables_json)

            await ctx.send(embed=success_embed("Timetable set."))

    else:
        await ctx.send(embed=error_embed("No attachments found."))
        return


@bot.command()
async def unset(ctx, user: discord.User = None):

    # Check if a user was passed.
    if user:
        if ctx.author.id != 277507281652940800:
            await ctx.send(embed=error_embed("You aren't Vidhan, you can't do that."))
    else:
        user = ctx.author

    # Check if user's timetable is set.
    if str(user.id) in timetables["users"].keys():

        timetables["users"].pop(str(user.id))

        with open(join(dirname(__file__), "timetables.json"), "w") as timetables_json:
            json.dump(timetables, timetables_json)

        await ctx.send(embed=success_embed("Timetable unset."))

    else:
        await ctx.send(
            embed=error_embed("Your timetable is not set. Use `tt.set` to set it.")
        )
        return


@bot.command()
async def compare(ctx, user: discord.User = None):
    if str(ctx.author.id) in timetables["users"].keys():
        if user:
            users = [user]
        else:
            users = [
                await bot.fetch_user(user_id) for user_id in timetables["users"].keys()
            ]

        for user in users:
            if str(user.id) in timetables["users"].keys():
                shared_courses = []
                for semester in range(2):
                    for term in range(2):
                        for week in range(2):
                            for course in range(2):
                                if (
                                    timetables["users"][str(ctx.author.id)]["courses"][
                                        semester
                                    ][term][week][course]["course_code"]
                                    == timetables["users"][str(user.id)]["courses"][
                                        semester
                                    ][term][week][course]["course_code"]
                                ):
                                    shared_courses.append(
                                        {
                                            "user": user,
                                            "name": timetables["users"][str(user.id)][
                                                "name"
                                            ],
                                            "semester": semester,
                                            "term": term,
                                            "week": week,
                                            "course": timetables["users"][
                                                str(ctx.author.id)
                                            ]["courses"][semester][term][week][course],
                                        }
                                    )
                if shared_courses:
                    if user.id != ctx.author.id:
                        await ctx.author.send(
                            embed=generate_shared_courses_embed(shared_courses)
                        )
        await ctx.send(
            embed=success_embed(
                "If you share courses with anyone in the server (or the person you mentioned), you will recieve the shared courses in your DMs."
            )
        )

    else:
        await ctx.send(
            embed=error_embed("Your timetable is not set. Use `tt.set` to set it.")
        )


@bot.command()
async def classes(ctx, user: discord.User = None):

    # Check if a user was passed.
    if user:
        if ctx.author.id != 277507281652940800:
            await ctx.send(embed=error_embed("You aren't Vidhan, you can't do that."))
    else:
        user = ctx.author

    if str(user.id) in timetables["users"].keys():
        user_dict = copy.deepcopy(timetables["users"][str(user.id)])
        user_dict["user"] = user
        for user_ in [
            await bot.fetch_user(user_id) for user_id in timetables["users"].keys()
        ]:
            if str(user.id) in timetables["users"].keys():
                for semester in range(2):
                    for term in range(2):
                        for week in range(2):
                            for course in range(2):
                                if (
                                    "shared_with"
                                    not in user_dict["courses"][semester][term][week][
                                        course
                                    ].keys()
                                ):
                                    user_dict["courses"][semester][term][week][course][
                                        "shared_with"
                                    ] = []
                                if (
                                    timetables["users"][str(user.id)]["courses"][
                                        semester
                                    ][term][week][course]["course_code"]
                                    == timetables["users"][str(user_.id)]["courses"][
                                        semester
                                    ][term][week][course]["course_code"]
                                ):
                                    user_dict["courses"][semester][term][week][course][
                                        "shared_with"
                                    ].append(user_)

        await ctx.author.send(embed=generate_shared_students_embed(user_dict))
        await ctx.send(
            embed=success_embed("You will recieve your classes in your DMs.")
        )

    else:
        await ctx.send(
            embed=error_embed("Your timetable is not set. Use `tt.set` to set it.")
        )


@bot.command()
async def courses(ctx, user: discord.User = None):

    # Check if a user was passed.
    if not user:
        user = await bot.fetch_user(ctx.author.id)

    if str(user.id) in timetables["users"].keys():

        user_dict = copy.deepcopy(timetables["users"][str(user.id)])
        user_dict["user"] = user
        await ctx.author.send(embed=generate_courses_embed(user_dict))
        await ctx.send(
            embed=success_embed("You will recieve your courses in your DMs.")
        )

    else:
        await ctx.send(
            embed=error_embed("Your timetable is not set. Use `tt.set` to set it.")
        )
        return


bot.run(BOT_TOKEN)
