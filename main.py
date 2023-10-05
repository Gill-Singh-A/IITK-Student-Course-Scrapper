#! /usr/bin/env python3

import requests, pickle
from datetime import date
from bs4 import BeautifulSoup
from optparse import OptionParser
from time import strftime, localtime
from colorama import Fore, Back, Style

status_color = {
    '+': Fore.GREEN,
    '-': Fore.RED,
    '*': Fore.YELLOW,
    ':': Fore.CYAN,
    ' ': Fore.WHITE
}

tag_id = {0: "Academic Session",
          1: "Semester",
          2: "Course ID",
          3: "Course Name",
          4: "Instructor",
          5: "Department"}

def display(status, data, start='', end='\n'):
    print(f"{start}{status_color[status]}[{status}] {Fore.BLUE}[{date.today()} {strftime('%H:%M:%S', localtime())}] {status_color[status]}{Style.BRIGHT}{data}{Fore.RESET}{Style.RESET_ALL}", end=end)

def get_arguments(*args):
    parser = OptionParser()
    for arg in args:
        parser.add_option(arg[0], arg[1], dest=arg[2], help=arg[3])
    return parser.parse_args()[0]

if __name__ == "__main__":
    data = get_arguments(('-l', "--load", "load", "File of Roll Numbers to load (pickle file)"),
                         ('-w', "--write", "write", "Name of the File for the data to be dumped (default=current data and time)"))
    if not data.load:
        display('-', f"Please specify the file of roll numbers to Load!")
        exit(0)
    else:
        try:
            display(':', f"Loading File {Back.MAGENTA}{data.load}{Back.RESET}")
            with open(data.load, 'rb') as file:
                student_data = pickle.load(file)
            display('+', f"Loaded File {Back.MAGENTA}{data.load}{Back.RESET}")
        except FileNotFoundError:
            display('-', f"File {Back.MAGENTA}{data.load}{Back.RESET} not found")
            exit(0)
        except:
            display('-', f"Error while reading File {Back.MAGENTA}{data.load}{Back.RESET}")
            exit(0)
    if not data.write:
        data.write = f"{date.today()} {strftime('%H_%M_%S', localtime())}"
    courseDetails = {}
    for index, roll in enumerate(student_data):
        course_details = []
        response = requests.get(f"http://172.26.142.68/dccourse/studdc.php?roll_no={roll}")
        page = BeautifulSoup(response.text, "html.parser")
        tr_tags = page.find_all("tr")[1:]
        for tr_tag in tr_tags:
            course_detail = {}
            td_tags = tr_tag.find_all("td")
            tag_range = len(tag_id) if len(tag_id) < len(td_tags) else len(td_tags)
            try:
                for tag_index in range(tag_range):
                    course_detail[tag_id[tag_index]] = td_tags[tag_index].text.strip()
            except:
                display('-', f"Error while Scrapping the Data of {Back.MAGENTA}{roll}{Back.RESET}", start='\r')
                continue
            course_details.append(course_detail)
        courseDetails[roll] = course_details
        display('*', f"Entities Scrapped = {Back.MAGENTA}{index+1}/{len(student_data)} ({(index+1)/len(student_data)*100:.2f}%){Back.RESET}", start='\r', end='')
    display(':', f"Dumping Data to {Back.MAGENTA}{data.write}{Back.RESET}", start='\n')
    with open(f"{data.write}", 'wb') as file:
        pickle.dump(courseDetails, file)
    display('+', f"Dumped Data to {Back.MAGENTA}{data.write}{Back.RESET}")