import icalendar
import pandas as pd
import datetime

FILE_PATH_TO_CALENDAR = r'C:\Users\joel.braganzamendes\OneDrive - Multiverse\Documents\CoachCoverCalendar0112v3.ics'
QUARTER_START = datetime.datetime(2024,1,1,tzinfo=datetime.timezone.utc)

def control_format(method):
    def wrapper(*args, **kwargs):
        result = method(*args, **kwargs)

        if args[2].lower() == 'coach':
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


        # Perform some actions after the method call
        # if method.__name__.startswith("extract_"):
        #     assert isinstance(result, (datetime.datetime, str, list)), "TypeError: Error in data extraction"
            
        # if method.__name__.endswith("coach"):
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
    # @control_format
    # def extract_coach(self, slot: icalendar.Event) -> (str, list):
    #     '''gets the coach information from a calendar event'''
    #     event_attendees = (
    #         "mailto:no cover@multiverse.io"
    #         if slot.get("ATTENDEE") == None
    #         else slot.get("ATTENDEE")
    #     ) # if there is no coach we want to reassign/check for 'no cover'
    #     return event_attendees

    # @control_format
    # def extract_time(self, slot):
    #     # Getting time information code here

    # @control_format
    # def extract_date(self, slot):
    #     # Getting date information code here

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
    
cover = MyCalendar(FILE_PATH_TO_CALENDAR)
#n = 0
for event in cover.calendar.walk('VEVENT'):
    #print( type(event.get("DTSTART").dt) is datetime.datetime and event.get("DTSTART").dt >= QUARTER_START)
    if cover.valid_slot(event):
        print(cover.extract(event,'Coach'),cover.extract(event,'TIME'),cover.extract(event,'date'))
    # n += 1
    # if n == 40:
    #     break