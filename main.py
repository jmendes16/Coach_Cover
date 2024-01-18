from iCalMod import *

FILE_PATH_TO_CALENDAR = 'path/to/your/calendar.ics'
QUARTER_START = datetime.datetime('your_year','your_month',1,tzinfo=datetime.timezone.utc)

if __name__ == '__main__':
    cover = MyCalendar(FILE_PATH_TO_CALENDAR)
    event_table = EventTable(QUARTER_START)

    for event in cover.slots():
        if cover.valid_slot(event):
            event_table.set_coach(cover.get_slot_data(event))

    event_table.reset_index(drop=True, inplace=True) # adding new rows makes for an ugly index on the output
    print(event_table.head()) # for troubleshooting

    event_table.to_csv('path/to/your/output.csv')
