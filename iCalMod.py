import icalendar
import pandas as pd
import datetime

FILE_PATH_TO_CALENDAR = 'path/to/calendar/file.ics'
QUARTER_START = datetime.datetime('your_year','your_month',1,tzinfo=datetime.timezone.utc)

def control_format(method):
    '''decorator for formatting output when extracting data from calendar'''
    def wrapper(*args, **kwargs):
        result = method(*args, **kwargs)

        if args[2].lower() == 'coach':
            # formats coaches as a list of lower case strings
            if result is None:
                return ['no cover']
            elif isinstance(result, str):
                return [result[7:-14].replace('.',' ')]
            elif isinstance(result, list):
                return [i[7:-14].replace('.',' ') for i in result]
        elif args[2].lower() == 'time':
            return 'am' if result.dt.hour == 9 else 'pm'
        elif args[2].lower() == 'date':
            return result.dt.date()
        else:
            print('ICSError: Error retrieving data from calendar file. Potentially requested additional data')
            return result
    return wrapper

class CalendarTool:
    def get_quarter_end(self, start_date: datetime) -> datetime:
        '''calculate the final day of the quarter'''
        if (start_date.month) == 10:
            end_date = datetime.datetime(
                start_date.year, 12, 24, tzinfo=datetime.timezone.utc
            ) # this is to account for company Christmas shutdown
        elif (start_date.month) == 1:
            end_date = datetime.datetime(
                start_date.year, 3, 31, tzinfo=datetime.timezone.utc
            ) # since March is the only quarter ending on the 31st
        else:
            end_date = datetime.datetime(
                start_date.year, start_date.month + 2, 30, tzinfo=datetime.timezone.utc
            )
        return end_date

class MyCalendar(icalendar.Calendar, CalendarTool): # cover = MyCalendar(FILE_PATH_TO_CALENDAR)

    def __init__(self, file_path: str):
        super().__init__()

        with open(file_path) as f:
            self.calendar = icalendar.Calendar.from_ical(f.read())

    def valid_slot(self, slot: icalendar.Event) -> bool:
        '''checks if an event on the calendar is valid.  ics files include additional events for recurring meetings etc.'''
        valid = (
            type(slot.get("DTSTART").dt) is datetime.datetime # datetime is a subclass of date so require type rather than isinstance
            and slot.get("TRANSP") == "OPAQUE" # this appears more in earlier quarters but may still come up
            and slot.get("RRULE") is None # this gets rid of the recurrence rule events that always contain no coaches
            and slot.get("DTSTART").dt >= QUARTER_START
            and slot.get("DTSTART").dt <= self.get_quarter_end(QUARTER_START)
        )
        return valid

    @control_format
    def extract(self, slot: icalendar.Event, detail: str) -> (str, list, datetime.datetime):
        if detail.lower() == 'coach':
            return slot.get('ATTENDEE')
        elif detail.lower() == 'time':
            return slot.get('DTSTART')
        elif detail.lower() == 'date':
            return slot.get('DTSTART')
        else:
            return slot.get(detail)

# test for MyCalendar class    
# cover = MyCalendar(FILE_PATH_TO_CALENDAR)

# for event in cover.calendar.walk('VEVENT'):
#     if cover.valid_slot(event):
#         print(cover.extract(event,'Coach'),cover.extract(event,'TIME'),cover.extract(event,'date'))
