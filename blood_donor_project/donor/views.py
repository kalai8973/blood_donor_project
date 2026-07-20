from django.shortcuts import render, redirect
from .forms import DonorForm, BloodRequestForm
from .models import Donor
from django.shortcuts import get_object_or_404
from .models import Donor, BloodRequest
from django.db.models import Count
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from openpyxl import Workbook
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


def register_donor(request):

    if request.method == 'POST':

        form = DonorForm(request.POST)

        if form.is_valid():

            donor = form.save()

            # Send Welcome Email
            send_mail(

                subject='🩸 Welcome to Blood Donor Finder',

                message=f'''
Hello {donor.name},

Thank you for registering as a Blood Donor.

Your willingness to donate blood can save someone's life.

----------------------------------------

Your Details

Name         : {donor.name}
Blood Group  : {donor.blood_group}
City         : {donor.city}

----------------------------------------

Stay Healthy.
Stay Safe.
Save Lives.

Regards,

Blood Donor Finder Team
''',

                from_email=settings.EMAIL_HOST_USER,

                recipient_list=[donor.email],

                fail_silently=True,

            )

            return redirect('register')

    else:

        form = DonorForm()

    return render(request, 'register.html', {'form': form})

def donor_list(request):
    donors = Donor.objects.all()
    return render(request, 'donors.html', {'donors': donors})


def search_donor(request):

    donors = Donor.objects.none()

    blood_group = request.GET.get('blood_group')
    city = request.GET.get('city')

    if blood_group and city:

        donors = Donor.objects.filter(
            blood_group=blood_group,
            city__icontains=city
        )

    return render(request, 'search.html', {'donors': donors})


def blood_request(request):

    if request.method == 'POST':

        form = BloodRequestForm(request.POST)

        if form.is_valid():

            blood_request = form.save()

            send_mail(
    subject='🩸 Blood Donor Finder - Request Received',

    message=f'''
Hello,

Your blood request has been successfully submitted.

Patient Name : {blood_request.patient_name}
Blood Group  : {blood_request.blood_group}
Hospital     : {blood_request.hospital}

Our team will try to find matching donors as soon as possible.

Thank you for using Blood Donor Finder.

Regards,
Blood Donor Finder Team
''',

    from_email=settings.EMAIL_HOST_USER,

    recipient_list=[settings.EMAIL_HOST_USER],

    fail_silently=True,

            )

            return redirect('request_blood')

    else:

        form = BloodRequestForm()

    return render(
        request,
        'blood_request.html',
        {'form': form}
    )
def home(request):
   

    total_donors = Donor.objects.count()
    total_requests = BloodRequest.objects.count()
    available = Donor.objects.filter(availability=True).count()
    cities = Donor.objects.values('city').distinct().count()

    context = {
        'total_donors': total_donors,
        'total_requests': total_requests,
        'available': available,
        'cities': cities,
    }

    return render(request, 'home.html', context)
    
def edit_donor(request, id):

    donor = get_object_or_404(Donor, id=id)

    if request.method == 'POST':
        form = DonorForm(request.POST, instance=donor)

        if form.is_valid():
            form.save()
            return redirect('donors')

    else:
        form = DonorForm(instance=donor)

    return render(request, 'edit_donor.html', {'form': form})    
def delete_donor(request, id):

    donor = Donor.objects.get(id=id)
    donor.delete()

    return redirect('donors')   
def dashboard(request):

    total_donors = Donor.objects.count()
    total_requests = BloodRequest.objects.count()
    available = Donor.objects.filter(availability=True).count()
    unavailable = Donor.objects.filter(availability=False).count()

    recent_donors = Donor.objects.order_by('-id')[:5]

    blood_data = Donor.objects.values('blood_group').annotate(
        total=Count('blood_group')
    )

    labels = []
    values = []

    for item in blood_data:
        labels.append(item['blood_group'])
        values.append(item['total'])

    context = {
        'total_donors': total_donors,
        'total_requests': total_requests,
        'available': available,
        'unavailable': unavailable,
        'recent_donors': recent_donors,
        'labels': labels,
        'values': values,
    }

    return render(request, 'dashboard.html', context)
def export_pdf(request):

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Blood_Donor_Report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)

    data = [
        ['Name', 'Email', 'Mobile', 'City', 'Blood Group']
    ]

    donors = Donor.objects.all()

    for donor in donors:
        data.append([
            donor.name,
            donor.email,
            donor.mobile,
            donor.city,
            donor.blood_group
        ])

    table = Table(data)

    style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.red),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),

        ('GRID', (0,0), (-1,-1), 1, colors.black),

        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),

        ('BACKGROUND', (0,1), (-1,-1), colors.beige),

        ('ALIGN', (0,0), (-1,-1), 'CENTER'),

        ('BOTTOMPADDING', (0,0), (-1,0), 10),
    ])

    table.setStyle(style)

    elements = [table]

    doc.build(elements)

    return response    
def export_excel(request):

    workbook = Workbook()

    sheet = workbook.active

    sheet.title = "Blood Donors"

    sheet.append([
        "Name",
        "Email",
        "Mobile",
        "City",
        "Blood Group",
        "Availability"
    ])

    donors = Donor.objects.all()

    for donor in donors:

        sheet.append([

            donor.name,
            donor.email,
            donor.mobile,
            donor.city,
            donor.blood_group,
            "Available" if donor.availability else "Unavailable"

        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    response['Content-Disposition'] = 'attachment; filename=Blood_Donors.xlsx'

    workbook.save(response)

    return response
def login_user(request):

    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user:

            login(request, user)

            return redirect("dashboard")

    return render(request, "login.html")


def logout_user(request):

    logout(request)

    return redirect("login")  
def about(request):
    return render(request, 'about.html')   
def contact(request):
    return render(request, 'contact.html')       