import re
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.template import Context, loader


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


def check_mentions(comment, author, document):
    username_re = re.compile(r'@\w+')
    users_mentioned = username_re.findall(comment)
    if users_mentioned:
        users_mentioned = map(lambda x: x[1:], username_re.findall(comment))
        email_content = create_email(author, document)
        collaborators = document.document.get_users_with_perms()
        collaborator_names = [c.username for c in collaborators]
        username_targets = list(
            set(users_mentioned).intersection(collaborator_names)
        )
        user_targets = [
            User.objects.get(username=name) for name in username_targets
        ]
        emails = [u.email for u in user_targets]
        try:
            send_mail(
                settings.PROJECT_NAME + ' - %s has mentioned you' % author,
                email_content,
                settings.DEFAULT_FROM_EMAIL,
                emails,
                fail_silently=False
            )
        except Exception as e:
            'email could not be sent.'


def create_email(author, document):
    title = document.title
    filename = document.docfile_basename
    doc_url = get_absolute_url(reverse(
        "docviewer_viewer_view",
        kwargs={'pk': document.pk, 'slug': document.slug}
    ))
    template = loader.get_template('docviewer/email_mentions.html')
    context = Context({
        'username': author,
        'document': '{} - {}'.format(title, filename),
        'url': doc_url,
    })
    message = template.render(context)
    return message


def get_absolute_url(relative_url):
    SITE = Site.objects.get_current()
    if relative_url and (relative_url[0:7] == 'http://' or relative_url[0:8] == 'https://'):
        return relative_url
    return "http://%s%s" % (SITE.domain, relative_url)




