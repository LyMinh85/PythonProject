from datetime import datetime

intervals = (
    ('weeks', 604800),  # 60 * 60 * 24 * 7
    ('days', 86400),  # 60 * 60 * 24
    ('hours', 3600),  # 60 * 60
    ('minutes', 60),
    ('seconds', 1),
)


def to_date_obj(date_time_str):
    return datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')


def display_time(from_date, today=datetime.now(), granularity=1):
    result = []
    seconds = int((today - from_date).total_seconds())
    if seconds < 0:
        return 'Just now'
    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {} ago".format(value, name))
    return ', '.join(result[:granularity])
