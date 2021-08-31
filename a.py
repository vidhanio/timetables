import requests, io, discord, json, re, pprint
from discord.ext import commands
from os.path import join, dirname
from settings import *
from pdfminer.high_level import extract_pages, extract_text
from pdfminer.layout import LTTextBoxHorizontal


def validate_pdf(pdf_url: str):
    response = requests.get(pdf_url)
    pdf = io.BytesIO(response.content)

    if "Student Timetables" not in extract_text(pdf):
        return False
    else:
        return True


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


def generate_student_info(pdf_url: str):

    response = requests.get(pdf_url)
    pdf = io.BytesIO(response.content)

    for page_layout in extract_pages(pdf):
        for element in page_layout:
            if (
                isinstance(element, LTTextBoxHorizontal)
                and "Semester 1" in element.get_text()
            ):
                courses_element = element.get_text()

    courses_list = list(filter(validate_element, courses_element.split()))
    courses_list = [i.rstrip(",") for i in courses_list]
    student_number = courses_list.pop(0)

    course_codes = list(
        filter(
            re.compile("^[A-Z][A-Z][A-Z][0-9][A-Z][A-Z0-9]-[A-Z]$").match,
            courses_list,
        )
    )
    first_initials = list(
        filter(
            re.compile("^[A-Z]$").match,
            courses_list,
        )
    )

    rooms = list(
        filter(
            re.compile("^[0-9][0-9][0-9]$").match,
            courses_list,
        )
    )

    last_names = [
        item
        for item in courses_list
        if item not in course_codes + first_initials + rooms
    ]

    study_indexes = [i for i, x in enumerate(last_names) if x == "STUDY"]

    for i in study_indexes:
        course_codes.insert(i, "STUDY")
        first_initials.insert(i, "S")
        last_names[i] = "Study"
        rooms.insert(i, 0)

    order = [0, 4, 1, 5, 2, 6, 3, 7, 8, 12, 9, 13, 10, 14, 11, 15]

    courses_dict = {
        "course_codes": [course_codes[i] for i in order],
        "first_initials": [first_initials[i] for i in order],
        "last_names": [last_names[i] for i in order],
        "rooms": [rooms[i] for i in order],
    }

    student_info = {
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


pdf_url = "https://cdn.discordapp.com/attachments/667531473309663262/882229603723247626/lem8q1hgh.pdf"

response = requests.get(pdf_url)
pdf = io.BytesIO(response.content)

for page_layout in extract_pages(pdf):
    for element in page_layout:
        if isinstance(element, LTTextBoxHorizontal):
            print(element.get_text())
