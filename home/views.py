from django.contrib.auth.decorators import login_required
from home.models import colleges
from django.shortcuts import render, redirect
from home.models import Contact
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate
from home.models import EventPage
from django.core.mail import send_mail
import requests
from EventsForU import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from home.models import student
from django.utils.html import strip_tags
from_email = settings.EMAIL_HOST_USER

# Create your views here.


def index(request):
    event = EventPage.objects.all()

    events2021 = EventPage.objects.filter(eventyear=2021)
    events2023 = EventPage.objects.filter(eventyear=2023)
    college = colleges.objects.all()

    return render(request, 'index.html', {'event': event, 'events2021': events2021, 'events2023': events2023, 'colleges': college})


def gh(request):
    events2022 = EventPage.objects.filter(eventyear=2022)
    print(events2022)
    events2021 = EventPage.objects.filter(eventyear=2021)
    events2023 = EventPage.objects.filter(eventyear=2023)
    college = colleges.objects.all()

    return render(request, 'indexx.html', {'events2022': events2022, 'events2021': events2021, 'events2023': events2023, 'colleges': college})


def logincollege(request):
    if request.method == 'POST':
        username = request.POST["uniqueid"]
        password = request.POST["password"]

        user = auth.authenticate(username=username, password=password)

        if username is not None and password is not None:
            if user is not None:
                auth.login(request, user)
                messages.info(request, "Successfully logged in!")
                return redirect('college')
            else:
                messages.info(request, "invalid credentials")
                return redirect('logincollege')
    else:
        return render(request, 'logincollege.html')


@login_required(login_url="logincollege")
def college(request):
    coll = colleges.objects.get(uniqid=request.user.username)
    ev = EventPage.objects.filter(college=request.user.username)

    le = len(ev)
    return render(request, "college.html", {'college': coll, "noofevents": le, "eventss": ev})


def search(request):
    if request.method == 'POST':
        eventname = request.POST["eventname"]
        eventss = EventPage.objects.filter(title=eventname)
        return render(request, "indexx.html", {"eventss": eventss})
    return render(request, "indexx.html")


def login(request):
    if request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["password"]

        user = auth.authenticate(username=username, password=password)

        if username is not None and password is not None:
            if user is not None:
                auth.login(request, user)
                messages.info(request, "Successfully logged in!")
                return redirect('home')
            else:
                messages.info(request, "invalid credentials")
                return redirect('home')
    else:
        return render(request, 'login.html')


def signupcollege(request):
    if request.method == 'POST':
        username = request.POST["uniqueid"]
        firstname = request.POST["college"]
        email = request.POST["email"]
        password = request.POST["password"]
        # address = request.POST["address"]
        country = request.POST["country"]
        if User.objects.filter(email=email).exists():
            messages.info(request, 'Email already in use')
            return redirect('signupcollege')
        elif User.objects.filter(username=username).exists():
            messages.info(request, 'Uniqueid already in use')
            return redirect('signupcollege')
        else:
            user = User.objects.create_user(
                username=username, password=password, email=email, first_name=firstname)
            user.save()
            college = colleges.objects.create(
                name=firstname, email=email, uniqid=username, password=password, country=country)
            college.save()
            messages.info(
                request, 'Successfully Registered. You can now login to your account.')
            return redirect('college')

    else:
        return render(request, "logincollege.html")


@login_required(login_url="logincollege")
def registerevent(request):
    return render(request, "registerevent.html")


def signup(request):
    if request.method == 'POST':
        username = request.POST["username"]
        firstname = request.POST["firstname"]
        email = request.POST["email"]
        password = request.POST["password"]
        country = request.POST["country"]

        if User.objects.filter(email=email).exists():
            messages.info(request, 'Email already in use')
            return redirect('home')
        elif User.objects.filter(username=username).exists():
            messages.info(request, 'Username already in use')
            return redirect('home')
        else:
            user = User.objects.create_user(
                username=username, password=password, email=email, first_name=firstname)
            user.save()
            ussr = student.objects.create(
                email=email, username=username, password=password, country=country)
            ussr.save()
            messages.info(
                request, 'Successfully Registered. You can now login to your account.')
            return redirect('home')

    else:
        return render(request, "login.html")


def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        desc = request.POST.get('textbox')
        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        r = requests.post(
            'https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        if result['success']:
            contact = Contact(name=name, email=email, phone=phone, desc=desc)
            contact.save()
            messages.success(
                request, 'Your response has been sent! You will soon be recieving an email containing all the details. If you cannot find the email in your inbox, check the bulk or the junk folders.')
            event = EventPage.objects.get(id=desc)
            context = {
                "name": name,
                "phone": phone,
                "event": event.title,
                "location": event.location,
                "desc": event.desc,
                "organizer": event.organizer
            }
            message = render_to_string(
                'email/registration_complete_email.html', context)
            send_mail('Registration Completed | EventsForU',  strip_tags(
                message), 'ak21eeb0b08@student.nitw.ac.in', [email], fail_silently=False, html_message=message)
            return redirect('home')
        else:
            messages.error(request, 'Invalid reCAPTCHA. Please try again.')
            return redirect('contact')
    else:
        return render(request, "contact.html")


def eventpage(request, id):
    events = EventPage.objects.filter(id=id).first()
    return render(request, 'eventpage.html', {'events': events})


def logout(request):
    auth.logout(request)
    return redirect('/')


def logoutcollege(request):
    auth.logout(request)
    return redirect('/gh')


@login_required(login_url="logincollege")
def formevent(request):
    coll = colleges.objects.get(uniqid=request.user.username)

    eventdate = request.POST.get('name')
    eventday = request.POST.get('email')
    desc = request.POST.get('desc')
    title = request.POST.get('title')
    month = request.POST.get('month')
    year = request.POST.get('year')
    organizer = coll.name
    id = request.POST.get('id')
    createdat = request.POST.get('createdat')
    location = request.POST.get('locationr')
    tag = request.POST.get('tag')
    heading = request.POST.get('head')
    event = EventPage.objects.create(id=id, title=title.upper(), college=coll.uniqid, created_at=createdat, eventyear=year, eventmonth=month,
                                     organizer=coll.name, desc=desc, eventday=eventday, eventdate=eventdate, location=location, tag=tag, header=heading)
    event.save()
