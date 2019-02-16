from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.utils import timezone, translation
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.urls import reverse

from swingtime import forms as swingtime_forms
from swingtime import views as swingtime_views

from .forms import *
from .models import *


class TranslatedFormMixin(object):
    """
    Mixin that translates just the form for a FormView.

    Uses query_parameter attribute to determine which parameter to use for the
    language (defaults to 'language')
    """

    query_parameter = 'language'

    def set_language(self):
        # Changes the language to the one specified by query_parameter
        self.previous_language = translation.get_language()
        query_language = self.request.GET.get(self.query_parameter)

        if query_language:
            translation.activate(query_language)

    def wrap(self, method, *args, **kwargs):
        # Changes the language, calls the wrapped method, then reverts language
        self.set_language()

        return_value = method(*args, **kwargs)

        translation.activate(self.previous_language)

        return return_value

    def get_form(self, *args, **kwargs):
        # Wraps .get_form() in query_parameter language context.
        return self.wrap(super().get_form, *args, **kwargs)

    def post(self, *args, **kwargs):
        # Wraps .post() in query_parameter language context.
        return self.wrap(super().post, *args, **kwargs)


####################################################################
# Wrappers around swingtme views:
####################################################################

def atria_year_view(
    request,
    year,
    template='swingtime/yearly_view.html',
    queryset=None
):
    '''

    Context parameters:

    ``year``
        an integer value for the year in questin

    ``next_year``
        year + 1

    ``last_year``
        year - 1

    ``by_month``
        a sorted list of (month, occurrences) tuples where month is a
        datetime.datetime object for the first day of a month and occurrences
        is a (potentially empty) list of values for that month. Only months
        which have at least 1 occurrence is represented in the list

    '''
    return swingtime_views.year_view(request, year, template, queryset)


def atria_month_view(
    request,
    year,
    month,
    template='swingtime/monthly_view.html',
    queryset=None
):
    '''
    Render a tradional calendar grid view with temporal navigation variables.

    Context parameters:

    ``today``
        the current datetime.datetime value

    ``calendar``
        a list of rows containing (day, items) cells, where day is the day of
        the month integer and items is a (potentially empty) list of occurrence
        for the day

    ``this_month``
        a datetime.datetime representing the first day of the month

    ``next_month``
        this_month + 1 month

    ``last_month``
        this_month - 1 month

    '''
    return swingtime_views.month_view(request, year, month, template, queryset)


def atria_day_view(
    request,
    year,
    month,
    day,
    template='swingtime/daily_view.html',
    **params
):
    '''
    See documentation for function``_datetime_view``.

    '''

    namespace = request.session['URL_NAMESPACE']

    return swingtime_views.day_view(request, year, month, day, template,
                                    **params)


def atria_occurrence_view(
    request,
    event_pk,
    pk,
    template='swingtime/occurrence_detail.html',
    form_class=swingtime_forms.SingleOccurrenceForm
):
    '''
    View a specific occurrence and optionally handle any updates.

    Context parameters:

    ``occurrence``
        the occurrence object keyed by ``pk``

    ``form``
        a form object for updating the occurrence
    '''
    return swingtime_views.occurrence_view(request, event_pk, pk, template,
                                           form_class)


@login_required
def add_atria_event(
    request,
    template='swingtime/add_event.html',
    event_form_class=AtriaEventForm,
    recurrence_form_class=swingtime_forms.MultipleOccurrenceForm
):
    '''
    Add a new ``Event`` instance and 1 or more associated ``Occurrence``s.

    Context parameters:

    ``dtstart``
        a datetime.datetime object representing the GET request value if
        present, otherwise None

    ``event_form``
        a form object for updating the event

    ``recurrence_form``
        a form object for adding occurrences

    '''
    return swingtime_views.add_event(request, template, event_form_class,
                                     recurrence_form_class)


####################################################################
# Atria custom views:
####################################################################

class SignupView(CreateView):
    # form_class = SignUpForm
    form_class = SignUpForm
    model = get_user_model()
    template_name = 'registration/signup.html'

    def get_success_url(self):
        return reverse('landing_page')


def signup_view(request):
    DEFAULT_ROLE = 'Attendee'

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)

            # add default role of 'Attendee' to new user registrations (additional roles can be added later)
            user.add_role(self.DEFAULT_ROLE)
            user.save()

            # need to auto-login with Atria custom user
            # login(request, user)
            return redirect('landing_page')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


def landing_page(request):
    """Landing page shell view."""
    # if user is not logged in, direct them to the landing page
    if not request.user.is_authenticated:
        print('User is not authenticated')
        clear_user_session(None, request.user, request)
        return render(request, 'atriacalendar/landing_page.html',
                      context={'active_view': 'landing_page'})

    # if user has a selected role (and org) direct them to appropriate dashboard
    if 'ACTIVE_ROLE' in request.session:
        role = request.session['ACTIVE_ROLE']
        if 'URL_NAMESPACE' not in request.session:
            request.session['URL_NAMESPACE'] = url_namespace(role)
        namespace = request.session['URL_NAMESPACE']
        print('ACTIVE_ROLE = ', role)
        if role == 'Admin':
            return render(request, 'atriacalendar/calendar_home.html',
                          context={'active_view': namespace + 'calendar_home'})
        else:
            return render(request, 'atriacalendar/calendar_home.html',
                          context={'active_view': namespace + 'calendar_home'})

    # if user is logged in without a selected role/org, set (if possible) and re-direct
    print('No ACTIVE_ROLE, try to set ...')
    init_user_session(None, request.user, request)

    # TODO if more than one role/org option, ask user to select

    role = request.session['ACTIVE_ROLE']
    namespace = request.session['URL_NAMESPACE']
    print('ACTIVE_ROLE = ', role)

    return render(request, 'atriacalendar/calendar_home.html',
                  context={'active_view': namespace + 'calendar_home'})


@login_required
def calendar_home(request):
    """Home page shell view."""

    namespace = request.session['URL_NAMESPACE']

    return render(request, 'atriacalendar/calendar_home.html',
                  context={'active_view': namespace + 'calendar_home'})


def calendar_view(request, *args, **kwargs):
    """Whole Calendar shell view."""

    the_year = kwargs['year']
    the_month = kwargs['month']

    namespace = request.session['URL_NAMESPACE']

    return render(request, 'atriacalendar/calendar_view.html',
                  context={'active_view': namespace + 'calendar_view', 'year': the_year,
                           'month': the_month})


@login_required
def create_event(request):
    """Create Calendar Event shell view."""

    namespace = request.session['URL_NAMESPACE']

    return render(request, 'atriacalendar/create_event.html',
                  context={'active_view': namespace + 'create_event'})


@login_required
def add_participants(request):
    """Second step of Event creation, adding participants. Shell view."""

    return render(request, 'atriacalendar/add_participants.html')


def event_list(request):
    """List/Manage Calendar Events shell view."""

    namespace = request.session['URL_NAMESPACE']

    return render(request, 'atriacalendar/event_list.html',
                  context={'active_view': namespace + 'calendar_list'})


def event_detail(request):
    """Shell view for viewing/editing a single Event."""

    return render(request, 'atriacalendar/event_detail.html')


def event_view(request, pk):
    lang = request.GET.get('event_lang')

    if lang:
        translation.activate(lang)

    return swingtime_views.event_view(request, pk, event_form_class=EventForm,
                                      recurrence_form_class=EventForm)


class EventListView(ListView, LoginRequiredMixin):
    """
    View for listing all events, or events by type
    """
    model = AtriaEvent
    paginate_by = 25
    context_object_name = 'events'

    def get_queryset(self):
        if 'event_type' in self.kwargs and self.kwargs['event_type']:
            return AtriaEvent.objects.filter(
                event_type=self.kwargs['event_type'])
        else:
            return AtriaEvent.objects.all()


class EventUpdateView(TranslatedFormMixin, UpdateView, LoginRequiredMixin):
    """
    View for viewing and updating a single Event.
    """
    form_class = AtriaEventForm
    model = AtriaEvent
    recurrence_form_class = swingtime_forms.MultipleOccurrenceForm
    template_name = 'swingtime/event_detail.html'
    query_parameter = 'event_lang'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        if self.form_class == self.recurrence_form_class:
            # There's been a validation error in the recurrence form
            context_data['recurrence_form'] = context_data['form']
            context_data['event_form'] = EventForm(instance=self.object)
        else:
            context_data['recurrence_form'] = self.recurrence_form_class(
                initial={'dstart': timezone.now()})
            context_data['event_form'] = context_data['form']

        return context_data

    def post(self, *args, **kwargs):
        # Selects correct form class based on POST data.
        # NOTE: lifted from swingtime.views.event_view
        # TODO: make the recurrence form POST to a different URL to clean this
        #       up
        if '_update' in self.request.POST:
            return super().post(*args, **kwargs)
        elif '_add' in self.request.POST:
            self.form_class = self.recurrence_form_class
            return super().post(*args, **kwargs)
        else:
            return HttpResponseBadRequest('Bad Request')


# design v2
def landing_v2(request):
    return render(request, 'atriacalendar/landing_page_v2.html')

def dashboard_v2(request):
    return render(request, 'atriacalendar/dashboard_v2.html')
