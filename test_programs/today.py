import calendar
from datetime import datetime
import subprocess
import sys

# Function to install packages
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Try to import colorama, and install if it is not installed
try:
    from colorama import Fore, Style, init
except ImportError:
    print("colorama not found. Installing...")
    install("colorama")
    from colorama import Fore, Style, init

# Initialize colorama
init()

def generate_ascii_calendar(year, month):
    # Create a Calendar object
    cal = calendar.Calendar(calendar.SUNDAY)
    
    # Get the current date
    today = datetime.now()
    current_day = today.day if today.year == year and today.month == month else None

    # Get the month's calendar
    month_calendar = cal.monthdayscalendar(year, month)

    # Start generating ASCII art calendar
    month_name = calendar.month_name[month]
    print(f"{month_name} {year}".center(28))
    print("Su Mo Tu We Th Fr Sa")
    
    for week in month_calendar:
        week_str = ''
        for day in week:
            if day == 0:
                week_str += '   '  # Empty day
            elif day == current_day:
                # Highlight the current day
                week_str += f"{Fore.RED}{day:2}{Style.RESET_ALL} "
            else:
                week_str += f"{day:2} "
        print(week_str)

# Set the current year and month
now = datetime.now()
year = now.year
month = now.month

# Generate the ASCII art calendar for the current month
generate_ascii_calendar(year, month)
