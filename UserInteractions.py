from datetime import datetime, timezone

def current_quarter_start(datetime_now: datetime) -> datetime:
    year = datetime_now.year
    month = 3 * ((datetime_now.month - 1)//3) + 1
    return datetime(year,month,1,tzinfo=timezone.utc)

def next_quarter_start(datetime_now: datetime) -> datetime:
    current_quarter = current_quarter_start(datetime_now)
    next_quarter = datetime(
        current_quarter.year + int(current_quarter.month / 12), 
        (current_quarter.month % 12) + 3,
        1,
        tzinfo=timezone.utc
    )
    return next_quarter

def previous_quarter_start(datetime_now: datetime) -> datetime:
    current_quarter = current_quarter_start(datetime_now)
    previous_quarter = datetime(
        current_quarter.year - int(current_quarter.month < 4), 
        ((current_quarter.month - 3) % 12),
        1,
        tzinfo=timezone.utc
    )
    return previous_quarter

def quarter_select() -> datetime:
    choice = input(
        "Which quarter's data do you want? current (c), next (n), last (l)\n"
    )
    if choice[0].lower() == "c":
        return current_quarter_start(datetime.now())
    elif choice[0].lower() == "n":
        return next_quarter_start(datetime.now())
    elif choice[0].lower() == "l":
        return previous_quarter_start(datetime.now())
    else:
        raise AssertionError("option not correctly chosen")

def get_file_path() -> str:
    file_path = "/mnt/calendars/" 
    # will need to edit these or use the bind mount argument in docker run
    # -v absolute/path/to/your/folder:/mnt/calendars
    filename = input(
        "What is the name of the calendar file? (stored in downloads, including .ics)\n"
    ) # there is no error catching here
    return file_path + filename

def export_file_path() -> str:
    file_path = "/mnt/calendars/"
    # will need to edit these or use the bind mount argument in docker run
    # -v absolute/path/to/your/folder:/mnt/calendars
    filename = input(
        'What is the name of the export file? (stored in downloads, including .csv)\n'
    ) # there is no error catching here
    return file_path + filename