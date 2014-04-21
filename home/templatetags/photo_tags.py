"""
Calendar template tag
"""
from home.calendar import HTMLCalendar
from django import template
from datetime import date
from itertools import groupby
from django.conf import settings
from django.utils.html import conditional_escape as esc

register = template.Library()

def do_photo_calendar(parser, token):
    """
    The template tag's syntax is {% photo_calendar year month photo_list %}
    """

    try:
        tag_name, year, month, photo_list = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires three arguments" % token.contents.split()[0]
    return PhotoCalendarNode(year, month, photo_list)


class PhotoCalendarNode(template.Node):
    """
    Process a particular node in the template. Fail silently.
    """

    def __init__(self, year, month, photo_list):
        try:
            self.year = template.Variable(year)
            self.month = template.Variable(month)
            self.photo_list = template.Variable(photo_list)

        except ValueError:
            raise template.TemplateSyntaxError

    def render(self, context):
        try:
            # Get the variables from the context so the method is thread-safe.
            my_photo_list = self.photo_list.resolve(context)
            my_photo_list = my_photo_list
            my_year = self.year.resolve(context)
            my_month = self.month.resolve(context)
            cal = PhotoCalendar(my_photo_list)
            return cal.formatmonth(int(my_year), int(my_month))
        except ValueError:
            return
        except template.VariableDoesNotExist:
            return


class PhotoCalendar(HTMLCalendar):
    """
    Overload Python's calendar.HTMLCalendar to add the appropriate photos to
    each day's table cell.
    """

    def __init__(self, photos):
        super(PhotoCalendar, self).__init__()
        self.photos = self.group_by_day(photos)

    def formatday(self, day, weekday):
        if day != 0:
            cssclass = self.cssclasses[weekday]
            if date.today() == date(self.year, self.month, day):
                cssclass += ' today %s' % day
            if day in self.photos:
                cssclass += ' filled'
                body = ['<span>']
                for photo in self.photos[day]:
                    body.append('<span style="position:relative;"><span \
                            class="dayid" style="position:absolute;opacity:0;margin-top:40px;margin-left:40px;">%s</span>' % (day))
                    body.append('''
                        <a class='group3' href='/%s/daily-photo/lightbox/%s'><img title="%s" src="%s/%s_100x100" /><a/>''' %
                        (photo.user.username, photo.key,photo.heading,  settings.MEDIA_URL, photo.photo))
                    # body.append(esc(photo.series.primary_name))
                    body.append('</span>')
                body.append('</span>')
                return self.day_cell(cssclass, '<span id="%s" class="dayNumber"></span> %s' % (day, ''.join(body)))
            return self.day_cell(cssclass, '<span id="%s" class="dayNumberNoPhotos">%d</span>' % (day, day))
        return self.day_cell('noday', '&nbsp;')

    def formatmonth(self, year, month):
        self.year, self.month = year, month
        return super(PhotoCalendar, self).formatmonth(year, month)

    def group_by_day(self, photos):
        field = lambda photo: photo.uploaded_on.day
        return dict(
            [(day, list(items)) for day, items in groupby(photos, field)]
        )

    def day_cell(self, cssclass, body):
        return '<td class="%s">%s</td>' % (cssclass, body)

# REGISTER the template tag so it is available to templates
register.tag("photo_calendar", do_photo_calendar)
