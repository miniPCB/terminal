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

def generate_ascii_calendar(year, month, highlight_day=None):
    """Generate a monthly ASCII calendar with optional day highlighting."""
    # Create a Calendar object
    cal = calendar.Calendar(calendar.SUNDAY)
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
            elif day == highlight_day:
                # Highlight the current day
                week_str += f"{Fore.RED}{day:2}{Style.RESET_ALL} "
            else:
                week_str += f"{day:2} "
        print(week_str)
    print()

def print_current_quarter():
    """Prints the three months of the current quarter with today highlighted."""
    # Get current date info
    now = datetime.now()
    year = now.year
    month = now.month
    current_day = now.day

    # Determine current quarter based on the current month
    if 1 <= month <= 3:
        quarter_months = [1, 2, 3]
    elif 4 <= month <= 6:
        quarter_months = [4, 5, 6]
    elif 7 <= month <= 9:
        quarter_months = [7, 8, 9]
    else:
        quarter_months = [10, 11, 12]

    # Print each month in the quarter
    for m in quarter_months:
        if m == month:
            generate_ascii_calendar(year, m, highlight_day=current_day)
        else:
            generate_ascii_calendar(year, m)

if __name__ == "__main__":
    print_current_quarter()
