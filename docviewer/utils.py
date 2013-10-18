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

def format_datetime_string(string):
    year = string[0:4]
    month = string[4:6]
    day = string[6:8]
    hour = string[8:10]
    minute = string[10:12]
    second = string[12:14]
    date = '{}-{}-{} {}:{}:{}'.format(
        year,
        month,
        day,
        hour,
        minute,
        second,
    )
    return date
