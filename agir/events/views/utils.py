from itertools import groupby
from collections import namedtuple


EventByDay = namedtuple("EventByDay", ["date", "events"])


def group_events_by_day(events):
    events_grouped = []
    for key, group in groupby(events, key=lambda event: event.start_time.date()):
        events_grouped.append(EventByDay(key, list(group)))
    return events_grouped
