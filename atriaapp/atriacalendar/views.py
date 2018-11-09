from django.shortcuts import render
from django.utils import translation

from swingtime import views as swingtime_views

from .forms import *


class TranslatedFormMixin(object):
    """
    Mixin that translates just the form for a FormView.

    Uses query_parameter attribute to determine which parameter to use for the
    language (defaults to 'langauge')
    """

    query_parameter = 'language'

    def get_form(self, *args, **kwargs):
        # Sets langauge before instantiating form, then reverts language
        current_language = translation.get_language()
        query_language = self.request.GET.get(self.query_parameter)

        if query_language:
            translation.activate(query_language)

        form = super().get_form(*args, **kwargs)

        translation.activate(current_language)

        return form


def login(request):
    """Shell login view."""

    return render(request, 'atriacalendar/login.html')

def calendar_home(request):
    """Home page shell view."""

    return render(request, 'atriacalendar/calendar_home.html',
                  context={'active_view': 'calendar_home'})

def calendar_view(request, *args, **kwargs):
    """Whole Calendar shell view."""

    the_year = kwargs['year']
    the_month = kwargs['month']

    return render(request, 'atriacalendar/calendar_view.html',
                  context={'active_view': 'calendar_view', 'year': the_year, 'month': the_month})

def create_event(request):
    """Create Calendar Event shell view."""

    return render(request, 'atriacalendar/create_event.html',
                  context={'active_view': 'create_event'})

def add_participants(request):
    """Second step of Event creation, adding participants. Shell view."""

    return render(request, 'atriacalendar/add_participants.html')

def event_list(request):
    """List/Manage Calendar Events shell view."""

    return render(request, 'atriacalendar/event_list.html',
                  context={'active_view': 'calendar_list'})

def event_detail(request):
    """Shell view for viewing/editing a single Event."""

    return render(request, 'atriacalendar/event_detail.html')

def event_view(request, pk):
    lang = request.GET.get('event_lang')

    if lang:
        translation.activate(lang)

    return swingtime_views.event_view(request, pk, event_form_class=EventForm,
                                      recurrence_form_class=EventForm)
