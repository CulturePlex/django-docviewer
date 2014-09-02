from datetime import datetime


def datetime_to_string(datetime):
    year = '{0:04}'.format(datetime.year)
    month = '{0:02}'.format(datetime.month)
    day = '{0:02}'.format(datetime.day)
    hour = '{0:02}'.format(datetime.hour)
    minute = '{0:02}'.format(datetime.minute)
    second = '{0:02}'.format(datetime.second)
    microsecond = '{0:06}'.format(datetime.microsecond)
    string = '{}{}{}{}{}{}{}'.format(
        year,
        month,
        day,
        hour,
        minute,
        second,
        microsecond
    )
    return string


def format_datetime_from_stringts(ts):
    year = ts[0:4]
    month = ts[4:6]
    day = ts[6:8]
    hour = ts[8:10]
    minute = ts[10:12]
    second = ts[12:14]
    microsecond = ts[14:20]
    string = '{}-{}-{}-{}-{}-{}-{}'.format(
        year,
        month,
        day,
        hour,
        minute,
        second,
        microsecond
    )
    return string


def format_datetime_string(string):
    months = {
        1: 'January',
        2: 'February',
        3: 'March',
        4: 'April',
        5: 'May',
        6: 'June',
        7: 'July',
        8: 'August',
        9: 'September',
        10: 'October',
        11: 'November',
        12: 'December',
    }
    year = string[0:4]
    month = string[4:6]
    day = string[6:8]
    hour = string[8:10]
    minute = string[10:12]
    second = string[12:14]
    hour = int(hour)
    if hour <= 12:
        am_pm = 'am'
    else:
        am_pm = 'pm'
    hour = hour % 12
    date = '{} {}, {} @ {}:{}:{} {}'.format(
        months[int(month)],
        day,
        year,
        hour,
        minute,
        second,
        am_pm,
    )
    return date


def format_datetimediff(datetimediff):
    total_seconds = int(datetimediff.total_seconds())
    seconds = total_seconds % 60
    total_minutes = total_seconds / 60
    minutes = total_minutes % 60
    total_hours = total_minutes / 60
    hours = total_hours % 24
    days = total_hours / 24
    
    secs_str, mins_str, hous_str, days_str = '', '', '', ''
    if seconds > 0:
        plural = ''
        if seconds > 1:
            plural = 's'
        secs_str = '{} second{}'.format(seconds, plural)
    if minutes > 0:
        plural = ''
        if minutes > 1:
            plural = 's'
        mins_str = '{} minute{}'.format(minutes, plural)
    if hours > 0:
        plural = ''
        if hours > 1:
            plural = 's'
        hous_str = '{} hour{}'.format(hours, plural)
    if days > 0:
        plural = ''
        if days > 1:
            plural = 's'
        days_str = '{} day{}'.format(days, plural)
    
    all_time_list = [days_str, hous_str, mins_str, secs_str]
    valid_time_list = [t for t in all_time_list if t]
    diff = ', '.join(valid_time_list)
    last_comma = diff.rfind(',')
    if last_comma != -1:
        diff = '{} and{}'.format(diff[0:last_comma], diff[last_comma+1:])
    
    return diff
