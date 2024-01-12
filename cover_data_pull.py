# import the required packages
import icalendar
import pandas as pd
import datetime

FILE_PATH_TO_CALENDAR = 'path/to/your/file.ics'
QUARTER_START = datetime.datetime('your_year','your_month',1,tzinfo=datetime.timezone.utc)

def load_calendar(FILE_PATH: str) -> icalendar.Calendar:
    '''open ical .ics file, will need to download this from DF Coach Cover settings and rename it.  Will also require full file path.  '''
    with open(FILE_PATH) as f:
        calendar = icalendar.Calendar.from_ical(f.read())
    return calendar

def get_quarter_end(start_date: datetime) -> datetime:
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
    
def create_events(start_date: datetime) -> pd.DataFrame:
    '''creates a dataframe containing all the cover slots in the specified quarter without a coach assigned'''
    all_dates = [
        start_date + datetime.timedelta(i)
        for i in range((get_quarter_end(start_date) - start_date).days + 1)
    ]
    cover_days = list(
        filter(lambda x: x.weekday() in [y for y in range(1, 5)], all_dates)
    ) # filtering out Monday, Saturday and Sunday
    df = pd.DataFrame(columns=["event_date", "event_time", "coach"])
    for day in cover_days:
        if day.weekday() == 4:
            df.loc[len(df)] = {
                "event_date": day.date(),
                "event_time": "am",
                "coach": 'no cover',
            } # making sure there is only one cover slot on Friday
        else:
            df.loc[len(df)] = {
                "event_date": day.date(),
                "event_time": "am",
                "coach": 'no cover',
            }
            df.loc[len(df)] = {
                "event_date": day.date(),
                "event_time": "pm",
                "coach": 'no cover',
            }
    return df


# create events function test
# print(create_events(QUARTER_START).head(15))

def event_booked(
    event_table: pd.DataFrame,
    event_date: datetime.datetime,
    event_time: str,
    coach_name: str,
) -> bool:
    '''checks if a coach is already assigned to a specific cover slot'''
    return (
        coach_name
        in event_table.loc[
            (event_table.event_date == event_date)
            & (event_table.event_time == event_time)
        ].coach.to_list()
    )

# event booked function test
# print(event_booked(create_events(QUARTER_START),datetime.date(2024,1,11),'am','no cover'))

def event_empty(
    event_table: pd.DataFrame,
    event_date: datetime.datetime,
    event_time: str
) -> bool:
    '''checks if a cover slot is unassigned'''
    return event_booked(
        event_table,
        event_date,
        event_time,
        'no cover'
    )

# event empty function test
# print(event_empty(create_events(QUARTER_START),datetime.datetime(2024,1,11,tzinfo=datetime.timezone.utc),'am'))

def valid_slot(slot: icalendar.Event) -> bool:
    '''checks if an event on the calendar is valid.  ics files include additional events for recurring meetings etc.'''
    valid = (
        type(slot.get("DTSTART").dt is datetime.datetime) # datetime is a subclass of date so require type rather than isinstance
        and slot.get("TRANSP") == "OPAQUE" # this appears more in earlier quarters but may still come up
        and slot.get("RRULE") is None # this gets rid of the recurrence rule events that always contain no coaches
        and slot.get("DTSTART").dt >= QUARTER_START
        and slot.get("DTSTART").dt <= get_quarter_end(QUARTER_START)
    )
    return valid

# valid slot function test
# test_calendar = load_calendar(FILE_PATH_TO_CALENDAR)
# n = 0
# for event in test_calendar.walk('VEVENT'):
#     print(event.get('DTSTART').dt,event.get('TRANSP'),event.get('RRULE'), event.get('ATTENDEE'))
#     print(valid_slot(event))
#     n += 1
#     if n == 20:
#         break

def extract_coach(slot: icalendar.Event) -> list:
    '''gets the coach information from a calendar event'''
    event_attendees = (
        "mailto:no cover@multiverse.io"
        if slot.get("ATTENDEE") == None
        else slot.get("ATTENDEE")
    ) # if there is no coach we want to reassign/check for 'no cover'
    coaches = []
    if isinstance(event_attendees, list):
        for attendee in event_attendees:
            coaches.append(attendee[7:-14])
    else:
        coaches.append(event_attendees[7:-14]) # this handles single coach and no coach bookings
    coaches = [coach.replace('.',' ') for coach in coaches]
    return coaches


def extract_time(slot: icalendar.Event) -> str:
    '''gets the time (am/pm) information from a calendar event'''
    event_time = slot.get('DTSTART').dt
    return 'am' if event_time.hour == 9 else 'pm'

def extract_date(slot: icalendar.Event) -> datetime.datetime:
    '''gets the date information from a calendar event'''
    return slot.get('DTSTART').dt.date()

def add_coaches(
    event_table: pd.DataFrame,
    event_date: datetime.datetime,
    event_time: str,
    coach_name: list,
) -> pd.DataFrame:
    '''adds/updates information in the event table dataframe'''
    for name in coach_name:
        if event_empty(
            event_table,
            event_date,
            event_time,
        ):
            event_table.loc[
                (event_table.event_date == event_date)
                & (event_table.event_time == event_time), 
                'coach'
            ] = name
        elif not event_booked(event_table, event_date, event_time, name):
            event_table.loc[len(event_table)] = {
                "event_date": event_date,
                "event_time": event_time,
                "coach": name,
            } # if not already assigned to a slot but someone else is we need to create a new entry in the table
    return event_table.sort_values('event_date')

if __name__ == '__main__':
    calendar = load_calendar(FILE_PATH_TO_CALENDAR)
    event_table = create_events(QUARTER_START)

    for event in calendar.walk('VEVENT'):
        if valid_slot(event):
            event_table = add_coaches(
                event_table,
                extract_date(event),
                extract_time(event),
                extract_coach(event)
            )
    event_table.reset_index(drop=True, inplace=True) # adding new rows makes for an ugly index on the output
    print(event_table.head()) # for troubleshooting

    event_table.to_csv('path/to/your/output.csv')
