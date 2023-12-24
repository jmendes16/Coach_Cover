# import the required packages
import icalendar
import pandas as pd
import datetime

# open ical .ics file, will need to download this from DF Coach Cover settings and rename it.  Will also require full file path.  
with open('path/to/file') as f:
    calendar = icalendar.Calendar.from_ical(f.read())

# create dataframe to store data and put in the date for the end of the previous quarter.  
df=pd.DataFrame(columns=['event_date','event_time','coach'])
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
