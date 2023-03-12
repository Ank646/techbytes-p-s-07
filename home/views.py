import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from django.http import FileResponse
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
    events2022 = EventPage.objects.filter(eventyear=2022)
    print(events2022)
    events2021 = EventPage.objects.filter(eventyear=2021)
    events2023 = EventPage.objects.filter(eventyear=2023)
    college = colleges.objects.all()

    return render(request, 'indexx.html', {'events2022': events2022, 'events2021': events2021, 'events2023': events2023, 'colleges': college})


# def gh(request):
#     events2022 = EventPage.objects.filter(eventyear=2022)
#     print(events2022)
#     events2021 = EventPage.objects.filter(eventyear=2021)
#     events2023 = EventPage.objects.filter(eventyear=2023)
#     college = colleges.objects.all()

#     return render(request, 'indexx.html', {'events2022': events2022, 'events2021': events2021, 'events2023': events2023, 'colleges': college})


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
        address = request.POST["address"]
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
                name=firstname, email=email, address=address, uniqid=username, password=password, country=country)
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
            return redirect('signup')
        elif User.objects.filter(username=username).exists():
            messages.info(request, 'Username already in use')
            return redirect('signup')
        else:
            user = User.objects.create_user(
                username=username, password=password, email=email, first_name=firstname)
            user.save()
            ussr = student.objects.create(
                email=email, username=username, password=password, country=country)
            ussr.save()
            messages.info(
                request, 'Successfully Registered. You can now login to your account.')
            return redirect('signup')

    else:
        return render(request, "login.html")


@login_required(login_url="login")
def myregev(request):
    name = request.user.username
    eventparticipate = Contact.objects.filter(name=name)
    hj = len(eventparticipate)
    return render(request, "myeventparticipate.html", {'part': eventparticipate, 'no': hj})


@login_required(login_url="login")
def contact(request):
    if request.method == "POST":
        id = request.POST.get('textbox')
        name = request.user.username
        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        r = requests.post(
            'https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        if result['success']:
            contact = Contact(
                name=name, email=request.user.email, desc=id)
            contact.save()
            messages.success(
                request, 'You are successfully registered for the events')
            event = EventPage.objects.get(id=id)
            event.participants = int(event.participants)+1
            event.save()

            context = {
                "name": name,

                "event": event.title,
                "location": event.location,
                "desc": event.desc,
                "organizer": event.organizer
            }
            buf = io.BytesIO()
            c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
            textob = c.beginText()
            textob.setTextOrigin(inch, inch)
            textob.setFont("Helvetica", 14)

            # filter it among ngo
            use = EventPage.objects.get(id=id)

            lines = []
            # Will Add All Progress Accordingly
            lines.append("Your name:    "+name)
            lines.append("Your email:    "+request.user.email)
            lines.append("=============================")
            lines.append("=============================")
            lines.append("You registered for :")

            lines.append("TYPE:    "+use.tag)
            lines.append("=============================")
            lines.append("=============================")
            lines.append("Organiser:   "+use.organizer)
            lines.append("Title:   "+use.title)
            lines.append("CITY:   "+use.location)
            lines.append("DATE:    "+str(use.eventday)+"/"+str(use.eventyear))
            lines.append("=============================")
            lines.append("=============================")
            lines.append("Description:     "+use.desc)

            lines.append("=============================")
            lines.append("=============================")

            for line in lines:
                textob.textLine(line)

            c.drawText(textob)
            c.showPage()
            c.save()
            buf.seek(0)

            return FileResponse(buf, as_attachment=True, filename="events"+id+".pdf")

            # message = render_to_string(
            #     'email/registration_complete_email.html', context)
            # send_mail('Registration Completed ',  strip_tags(
            #     message), 'ak21eeb0b08@student.nitw.ac.in', [email], fail_silently=False, html_message=message)
            return redirect('/')
        else:
            messages.error(request, 'Invalid reCAPTCHA. Please try again.')
            return redirect('contact')
    else:
        return render(request, "contact.html")


@login_required(login_url="logincollege")
def participants(request, evuu):
    eve = Contact.objects.filter(desc=evuu)
    eventt = EventPage.objects.get(id=evuu)
    length = len(eve)
    eventname = eventt.title
    return render(request, 'eventpart.html', {'eventparticipants': eve, 'eventname': eventname, 'noofparticipants': length})


@login_required(login_url="login")
def eventpage(request, id):
    events = EventPage.objects.get(id=id)
    registered = 0
    reg = Contact.objects.filter(desc=id, name=request.user.username)
    gh = len(reg)
    if gh != 0:
        registered = 1

    return render(request, 'eventpage.html', {'event': events, 'registered': registered})


@login_required(login_url="login")
def partevent(request, id):
    student = request.user.username
    studentemail = request.user.email
    if Contact.objects.filter(desc=id, name=student).exists():
        messages.info(request, "You have already registered for the event.")
        return redirect("/eventpage/"+id)
    else:
        contact = Contact(
            name=student, email=studentemail, desc=id)

        contact.save()
        messages.success(
            request, 'You are successfully registered for the events')
        event = EventPage.objects.get(id=id)
        event.participants = int(event.participants)+1
        event.save()

        context = {
            "name": student,

            "event": event.title,
            "location": event.location,
            "desc": event.desc,
            "organizer": event.organizer
        }
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
        textob = c.beginText()
        textob.setTextOrigin(inch, inch)
        textob.setFont("Helvetica", 14)

        # filter it among ngo
        use = EventPage.objects.get(id=id)

        lines = []
        lines.append("Your name:    "+student)
        lines.append("Your email:    "+request.user.email)
        lines.append("=============================")
        lines.append("=============================")
        lines.append("You registered for :")

        lines.append("TYPE:    "+use.tag)
        lines.append("=============================")
        lines.append("=============================")
        lines.append("Organiser:   "+use.organizer)
        lines.append("Title:   "+use.title)
        lines.append("CITY:   "+use.location)
        lines.append("DATE:    "+str(use.eventday)+"/" +
                     str(use.eventmonth)+"/"+str(use.eventyear))
        lines.append("=============================")
        lines.append("=============================")
        lines.append("Description:     "+use.desc)

        lines.append("=============================")
        lines.append("=============================")

        for line in lines:
            textob.textLine(line)

        c.drawText(textob)
        c.showPage()
        c.save()
        buf.seek(0)

        return FileResponse(buf, as_attachment=True, filename="events"+student+id+".pdf")

    # message = render_to_string(
    #     'email/registration_complete_email.html', context)
    # send_mail('Registration Completed ',  strip_tags(
    #     message), 'ak21eeb0b08@student.nitw.ac.in', [email], fail_silently=False, html_message=message)

    return render(request, "eventpage.html")


def logout(request):
    auth.logout(request)
    return redirect('/')


@login_required(login_url="login")
def cancelregistration(request, id):
    name = request.user.username
    email = request.user.email
    even = Contact.objects.get(name=name, desc=id, email=email)
    even.delete()
    event = EventPage.objects.get(id=id)

    event.participants = int(event.participants)-1
    event.save()
    messages.info(request, "Successfully unregistered for the event ")
    return redirect('/eventpage/'+id)


def logoutcollege(request):
    auth.logout(request)
    return redirect('/')


@login_required(login_url="login")
def collegeevent(request, colleve):
    col = EventPage.objects.filter(college=colleve)
    institute = colleges.objects.get(uniqid=colleve)
    return render(request, "collegeevent.html", {"collegeevents": col, "institutename": institute.name})


@login_required(login_url="logincollege")
def registerevent(request):
    if request.method == "POST":
        coll = colleges.objects.get(uniqid=request.user.username)

        eventdate = request.POST.get('date')
        eventday = request.POST.get('day')
        desc = request.POST.get('desc')
        title = request.POST.get('title')
        month = request.POST.get('month')
        year = request.POST.get('year')
        organizer = coll.name

        location = request.POST.get('location')
        tag = request.POST.get('tag')
        heading = request.POST.get('head')
        event = EventPage.objects.create(title=title.upper(), college=coll.uniqid,  eventyear=year, eventmonth=month,
                                         organizer=coll.name, desc=desc, eventday=eventday, eventdate=eventdate, location=location, tag=tag, header=heading)
        event.save()
        messages.success(request, "Event registered .....")

        return redirect("/registerevent")
    else:
        return render(request, "registerevent.html")
