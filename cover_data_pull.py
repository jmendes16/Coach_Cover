# import the required packages
import icalendar
import pandas as pd
import datetime

FILE_PATH_TO_CALENDAR = 'path/to/ics/file.ics'
QUARTER_START = datetime.datetime('your_year','your_month',1,tzinfo=datetime.timezone.utc)

def load_calendar(FILE_PATH: str) -> icalendar.Calendar:
    # open ical .ics file, will need to download this from DF Coach Cover settings and rename it.  Will also require full file path.  
    with open(FILE_PATH) as f:
        calendar = icalendar.Calendar.from_ical(f.read())
    return calendar

def get_quarter_end(start_date: datetime) -> datetime:
    if (start_date.month) == 10:
        end_date = datetime.datetime(
            start_date.year, 12, 24, tzinfo=datetime.timezone.utc
        )
    elif (start_date.month) == 1:
        end_date = datetime.datetime(
            start_date.year, 3, 31, tzinfo=datetime.timezone.utc
        )
    else:
        end_date = datetime.datetime(
            start_date.year, start_date.month + 2, 30, tzinfo=datetime.timezone.utc
        )
    return end_date
    
def create_events(start_date: datetime) -> pd.DataFrame:
    all_dates = [
        start_date + datetime.timedelta(i)
        for i in range((get_quarter_end(start_date) - start_date).days + 1)
    ]
    cover_days = list(
        filter(lambda x: x.weekday() in [y for y in range(1, 5)], all_dates)
    )
    df = pd.DataFrame(columns=["event_date", "event_time", "coach"])
    for day in cover_days:
        if day.weekday() == 4:
            df.loc[len(df)] = {
                "event_date": day.date(),
                "event_time": "am",
                "coach": None,
            }
        else:
            df.loc[len(df)] = {
                "event_date": day.date(),
                "event_time": "am",
                "coach": None,
            }
            df.loc[len(df)] = {
                "event_date": day.date(),
                "event_time": "pm",
                "coach": None,
            }
    return df


# function test
# print(create_events(QUARTER_START).head(15))

def event_booked(
    event_table: pd.DataFrame,
    event_date: datetime.datetime,
    event_time: str,
    coach_name: str,
) -> bool:
    return (
        coach_name
        in event_table.loc[
            (event_table.event_date == event_date)
            & (event_table.event_time == event_time)
        ].coach.to_list()
    )

# function test
# print(event_booked(create_events(QUARTER_START),datetime.date(2024,1,11),'am',None))

def event_empty(
    event_table: pd.DataFrame,
    event_date: datetime.datetime,
    event_time: str
) -> bool:
    return event_booked(
        event_table,
        event_date,
        event_time,
        None
    )

# function test
# print(event_empty(create_events(QUARTER_START),datetime.datetime(2024,1,11,tzinfo=datetime.timezone.utc),'am'))

def valid_slot(slot: icalendar.Event) -> bool:
    valid = (
        type(slot.get("DTSTART").dt is datetime.datetime)
        and slot.get("TRANSP") == "OPAQUE"
        and slot.get("RRULE") is None
        and slot.get("DTSTART").dt >= QUARTER_START
        and slot.get("DTSTART").dt <= get_quarter_end(QUARTER_START)
    )
    return valid

# function test
# test_calendar = load_calendar(FILE_PATH_TO_CALENDAR)
# n = 0
# for event in test_calendar.walk('VEVENT'):
#     print(event.get('DTSTART').dt,event.get('TRANSP'),event.get('RRULE'), event.get('ATTENDEE'))
#     print(valid_slot(event))
#     n += 1
#     if n == 20:
#         break

def extract_coach(slot: icalendar.Event) -> list:
    event_attendees = (
        "mailto:no cover@multiverse.io"
        if slot.get("ATTENDEE") == None
        else slot.get("ATTENDEE")
    )
    coaches = []
    if isinstance(event_attendees, list):
        for attendee in event_attendees:
            coaches.append(attendee[7:-14])
    else:
        coaches.append(event_attendees[7:-14])
    coaches = [coach.replace('.',' ') for coach in coaches]
    return coaches


def extract_time(slot: icalendar.Event) -> str:
    event_time = slot.get('DTSTART').dt
    return 'am' if event_time.hour == 9 else 'pm'

def extract_date(slot: icalendar.Event) -> datetime.datetime:
    return slot.get('DTSTART').dt.date()

def add_coaches(
    event_table: pd.DataFrame,
    event_date: datetime.datetime,
    event_time: str,
    coach_name: list,
) -> pd.DataFrame:
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
            }
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
    
    print(event_table.head())

    event_table.to_csv('your/desired/output/file.csv')

'''
# create dataframe to store data and put in the date for the end of the previous quarter.  
quarter_end=datetime.datetime(2023,9,30,tzinfo=datetime.timezone.utc)

# we can iterate through all the events in the calendar
for event in calendar.walk('VEVENT'):
    # first get the date of the event as this is our primary filter
    event_date=event.get('DTSTART').dt    

    # try block required for datetime errors, they come through as a mixture of datetime.date and datetime.datetime
    # this breaks the comparison
    try:
        if event_date > quarter_end:
            # event_summary=event.get('SUMMARY') # for DEBUG
            event_attendees='mailto:no cover@multiverse.io' if event.get('ATTENDEE') == None else event.get('ATTENDEE')
            event_time='am' if event_date.hour == 9 else 'pm'
            if isinstance(event_attendees, list):
                for attendee in event_attendees:
                    df.loc[len(df)]={'event_date':event_date.date(), 'event_time':event_time, 'coach':attendee[7:-14]}
                    #print(event_date, event_time, attendee[7:-14]) # for DEBUG
            else:
                df.loc[len(df)]={'event_date':event_date.date(), 'event_time':event_time, 'coach':event_attendees[7:-14]}
                #print(event_date, event_time, event_attendees[7:-14]) # for DEBUG
    except TypeError:
        continue
df.coach = df.coach.str.replace('.',' ')
df.head()

df.to_excel('CoachCoverQ3.xlsx') # this does add in some extra 'no covers' I assume this is when the recurring events are set up.
'''