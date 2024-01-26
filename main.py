from iCalMod import *
from UserInteractions import *

QUARTER = quarter_select()

if __name__ == '__main__':
    cover = MyCalendar(get_file_path())
    event_table = EventTable(QUARTER)

    for event in cover.slots():
        if cover.valid_slot(event, QUARTER):
            event_table.set_coach(cover.get_slot_data(event))

    event_table.reset_index(drop=True, inplace=True) # adding new rows makes for an ugly index on the output
    print(event_table.head()) # for troubleshooting

    event_table.to_csv(export_file_path())
