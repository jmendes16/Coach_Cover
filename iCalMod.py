import icalendar
import pandas as pd
import datetime

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

class MyCalendar(icalendar.Calendar, CalendarTool):

    def __init__(self, file_path: str):
        super().__init__()

        with open(file_path) as f:
            self.calendar = icalendar.Calendar.from_ical(f.read())

    def valid_slot(self, slot: icalendar.Event, start_date: datetime.datetime) -> bool:
        '''checks if an event on the calendar is valid.  ics files include additional events for recurring meetings etc.'''
        valid = (
            type(slot.get("DTSTART").dt) is datetime.datetime # datetime is a subclass of date so require type rather than isinstance
            and slot.get("TRANSP") == "OPAQUE" # this appears more in earlier quarters but may still come up
            and slot.get("RRULE") is None # this gets rid of the recurrence rule events that always contain no coaches
            and slot.get("DTSTART").dt >= start_date
            and slot.get("DTSTART").dt <= self.get_quarter_end(start_date)
        )
        return valid

    @control_format
    def extract(
        self, slot: icalendar.Event, detail: str
    ) -> (str, list, datetime.datetime):
        if detail.lower() == "coach":
            return slot.get("ATTENDEE")
        elif detail.lower() == "time":
            return slot.get("DTSTART")
        elif detail.lower() == "date":
            return slot.get("DTSTART")
        else:
            return slot.get(detail)

    def get_slot_data(self, slot: icalendar.Event) -> dict:
        '''gets data from calendar and returns it in a format designed for the events table'''
        return {
            'event_date':self.extract(slot, 'date'),
            'event_time':self.extract(slot, 'time'),
            'coach':self.extract(slot,'coach')
            }    

    def slots(self) -> icalendar.Event:
        '''generator function for events in calendar'''
        for slot in self.calendar.walk('VEVENT'):
            yield slot

class EventTable(pd.DataFrame,CalendarTool):

    def __init__(self, start_date: datetime.datetime):
        super().__init__(columns=["event_date", "event_time", "coach"])
        all_dates = [
        start_date + datetime.timedelta(i)
        for i in range((self.get_quarter_end(start_date) - start_date).days + 1)
        ]
        cover_days = list(
            filter(lambda x: x.weekday() in [y for y in range(1, 5)], all_dates)
        ) # filtering out Monday, Saturday and Sunday
        
        for day in cover_days:
            if day.weekday() == 4:
                self.loc[len(self)] = {
                    "event_date": day.date(),
                    "event_time": "am",
                    "coach": 'no cover',
                } # making sure there is only one cover slot on Friday
            else:
                self.loc[len(self)] = {
                    "event_date": day.date(),
                    "event_time": "am",
                    "coach": 'no cover',
                }
                self.loc[len(self)] = {
                    "event_date": day.date(),
                    "event_time": "pm",
                    "coach": 'no cover',
                }
    
    def event_booked(
        self,
        event_date: datetime.datetime,
        event_time: str,
        coach_name: str,
    ) -> bool:
        '''checks if a coach is already assigned to a specific cover slot'''
        return (
            coach_name
            in self.loc[
                (self.event_date == event_date)
                & (self.event_time == event_time)
            ].coach.to_list()
        )
    
    def event_empty(
        self,
        event_date: datetime.datetime,
        event_time: str
    ) -> bool:
        '''checks if a cover slot is unassigned'''
        return self.event_booked(
            event_date,
            event_time,
            'no cover'
        )
    
    def set_coach(
        self,
        event_data: dict
    ):
        '''adds/updates information in the event table dataframe'''
        for name in event_data['coach']:
            if self.event_empty(
                event_data['event_date'],
                event_data['event_time'],
            ):
                self.loc[
                    (self.event_date == event_data['event_date'])
                    & (self.event_time == event_data['event_time']), 
                    'coach'
                ] = name
            elif not self.event_booked(
                event_data['event_date'], event_data['event_time'], name
            ):
                self.loc[len(self)] = {
                    "event_date": event_data['event_date'],
                    "event_time": event_data['event_time'],
                    "coach": name,
                } # if not already assigned to a slot but someone else is we need to create a new entry in the table
        self.sort_values('event_date', inplace=True)
