import requests, io, discord, json, re, pprint
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
    courses_list = [i.rstrip(",") for i in courses_list]

    student_number = courses_list.pop(0)

    # Find course codes by matching regex pattern.
    course_codes = list(
        filter(
            re.compile("^[A-Z][A-Z][A-Z][0-9][A-Z][A-Z0-9]-[A-Z]$").match,
            courses_list,
        )
    )

    # Find first initials by matching regex pattern.
    first_initials = list(
        filter(
            re.compile("^[A-Z]$").match,
            courses_list,
        )
    )

    # Find rooms by matching by matching regex pattern.
    rooms = list(
        filter(
            re.compile("^[0-9][0-9][0-9]$").match,
            courses_list,
        )
    )

    # Last names are tricky because they do not match a pattern.
    # Instead, we just subtract all the already found information, and we are left with the last names.
    last_names = [
        item
        for item in courses_list
        if item not in course_codes + first_initials + rooms
    ]

    # If there are any study periods, add that information to all of the lists.
    study_indexes = [i for i, x in enumerate(last_names) if x == "STUDY"]

    for i in study_indexes:
        course_codes.insert(i, "STUDY")
        first_initials.insert(i, "S")
        last_names[i] = "Study"
        rooms.insert(i, 0)

    # This represents the order of the courses in relation to how they were parsed.
    order = [0, 4, 1, 5, 2, 6, 3, 7, 8, 12, 9, 13, 10, 14, 11, 15]

    # Order elements in correct order defined above.
    courses_dict = {
        "course_codes": [course_codes[i] for i in order],
        "first_initials": [first_initials[i] for i in order],
        "last_names": [last_names[i] for i in order],
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
                            "teacher": {"first_initial": "", "last_name": ""},
                            "room": 0,
                        },
                        {
                            "course_code": "",
                            "teacher": {"first_initial": "", "last_name": ""},
                            "room": 0,
                        },
                    ],
                    [
                        {
                            "course_code": "",
                            "teacher": {"first_initial": "", "last_name": ""},
                            "room": 0,
                        },
                        {
                            "course_code": "",
                            "teacher": {"first_initial": "", "last_name": ""},
                            "room": 0,
                        },
                    ],
                ],
                [
                    [
                        {
                            "course_code": "",
                            "teacher": {"first_initial": "", "last_name": ""},
                            "room": 0,
                        },
                        {
                            "course_code": "",
                            "teacher": {"first_initial": "", "last_name": ""},
                            "room": 0,
                        },
                    ],
                    [
                        {
                            "course_code": "",
                            "teacher": {"first_initial": "", "last_name": ""},
                            "room": 0,
                        },
                        {
                            "course_code": "",
                            "teacher": {"first_initial": "", "last_name": ""},
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
                            "teacher": {"first_initial": "", "last_name": ""},
                            "room": 0,
                        },
                        {
                            "course_code": "",
                            "teacher": {"first_initial": "", "last_name": ""},
                            "room": 0,
                        },
                    ],
                    [
                        {
                            "course_code": "",
                            "teacher": {"first_initial": "", "last_name": ""},
                            "room": 0,
                        },
                        {
                            "course_code": "",
                            "teacher": {"first_initial": "", "last_name": ""},
                            "room": 0,
                        },
                    ],
                ],
                [
                    [
                        {
                            "course_code": "",
                            "teacher": {"first_initial": "", "last_name": ""},
                            "room": 0,
                        },
                        {
                            "course_code": "",
                            "teacher": {"first_initial": "", "last_name": ""},
                            "room": 0,
                        },
                    ],
                    [
                        {
                            "course_code": "",
                            "teacher": {"first_initial": "", "last_name": ""},
                            "room": 0,
                        },
                        {
                            "course_code": "",
                            "teacher": {"first_initial": "", "last_name": ""},
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
                    student_info["courses"][semester][term][week][course]["teacher"][
                        "first_initial"
                    ] = courses_dict["first_initials"][counter]
                    student_info["courses"][semester][term][week][course]["teacher"][
                        "last_name"
                    ] = courses_dict["last_names"][counter]
                    student_info["courses"][semester][term][week][course][
                        "room"
                    ] = courses_dict["rooms"][counter]

                    counter += 1

    return student_info


# Allow bot to have all intents.
intents = discord.Intents.all()

# Set prefix.
bot = commands.Bot(command_prefix="tt!", intents=intents)

# Read from student_info.json to initialize info.
with open(join(dirname(__file__), "student_info.json"), "r") as student_info_json:
    student_info = json.load(student_info_json)


# tt!set: Set your timetable by uploading it in the same message as the command.
@bot.command(name="set")
async def _set(ctx, member: discord.Member = None):

    # Check if a member was passed.
    if member:
        if ctx.author.id != 277507281652940800:
            await ctx.send("Error: No permissions. :angry:")
    else:
        member = ctx.author

    # Check if message has attachments.
    if ctx.message.attachments:
        timetable_url = str(ctx.message.attachments[0])

        # Check if message has .pdf file extension.
        if timetable_url.lower()[-4:] != ".pdf":
            await ctx.send("Error: Attachment is not PDF. :confused:")
            return

        # Check if pdf is valid.
        elif not validate_pdf(timetable_url):
            await ctx.send("Error: PDF is not valid. :confused:")
            return

        # Generate student info and store it in dictionary, as well as writing it to the student_info.json.
        else:
            student_info["users"][str(member.id)] = generate_student_info(timetable_url)

            with open(
                join(dirname(__file__), "student_info.json"), "w"
            ) as student_info_json:
                json.dump(student_info, student_info_json)

            await ctx.send("Success: Timetable set! :smile:")

    else:
        await ctx.send("Error: No attachments. :confused:")
        return


@bot.command()
async def compare(ctx, member: discord.Member = None):
    if str(ctx.author.id) in student_info["users"].keys():
        if member:
            if str(member.id) in student_info["users"].keys():
                shared_courses = []
                for semester in range(2):
                    for term in range(2):
                        for week in range(2):
                            for course in range(2):
                                if (
                                    student_info["users"][str(ctx.author.id)][
                                        "courses"
                                    ][semester][term][week][course]
                                    == student_info["users"][str(member.id)]["courses"][
                                        semester
                                    ][term][week][course]
                                ):
                                    shared_courses.append(
                                        {
                                            "semester": semester + 1,
                                            "term": term + 1,
                                            "week": week + 1,
                                            "course": student_info["users"][
                                                str(ctx.author.id)
                                            ]["courses"][semester][term][week][course],
                                        }
                                    )
                if shared_courses:
                    shared_courses_string = (
                        "Congratulations, You share the following courses:\n"
                    )
                    for course in shared_courses:
                        shared_courses_string += (
                            "Semester {}, Week {}: {} ({})\n".format(
                                course["semester"],
                                course["week"],
                                course["course"]["course_code"],
                                course["course"]["teacher"]["last_name"],
                            )
                        )
                    await ctx.send(shared_courses_string)
                else:
                    await ctx.send("Unfortunately, you don't share any courses.")
            else:
                ctx.send(
                    "Error: {}'s timetable is not set. Ask them to use `tt!set` to set it. :confused:".format(
                        member.name
                    )
                )
        else:
            shared_courses_string = (
                "Congratulations, You share the following courses:\n"
            )
            for member in ctx.guild.members:
                if str(member.id) in student_info["users"].keys():
                    shared_courses = []
                    for semester in range(2):
                        for term in range(2):
                            for week in range(2):
                                for course in range(2):
                                    if (
                                        student_info["users"][str(ctx.author.id)][
                                            "courses"
                                        ][semester][term][week][course]
                                        == student_info["users"][str(member.id)][
                                            "courses"
                                        ][semester][term][week][course]
                                    ):
                                        shared_courses.append(
                                            {
                                                "semester": semester + 1,
                                                "term": term + 1,
                                                "week": week + 1,
                                                "course": student_info["users"][
                                                    str(ctx.author.id)
                                                ]["courses"][semester][term][week][
                                                    course
                                                ],
                                                "name": student_info["users"][
                                                    str(member.id)
                                                ]["name"],
                                            }
                                        )
                    if shared_courses:
                        if member.id != ctx.author.id:
                            shared_courses_string += "\n**{} ({})**:\n".format(
                                member.name, shared_courses[0]["name"]["first_name"]
                            )
                            for course in shared_courses:
                                shared_courses_string += (
                                    "Semester {}, Week {}: {} ({})\n".format(
                                        course["semester"],
                                        course["week"],
                                        course["course"]["course_code"],
                                        course["course"]["teacher"]["last_name"],
                                    )
                                )
            if (
                shared_courses_string
                == "Congratulations, You share the following courses:\n"
            ):
                await ctx.send(
                    "Unfortunately, you don't share courses with anyone in this server who has set their timetable."
                )
            else:
                await ctx.send(shared_courses_string)

    else:
        await ctx.send(
            "Error: Your timetable is not set, use `tt!set` to set it. :confused:"
        )


bot.run(BOT_TOKEN)
