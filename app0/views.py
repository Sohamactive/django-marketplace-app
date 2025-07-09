from urllib import request
from django.shortcuts import render,redirect,get_object_or_404
from .models import Registration, Enrollment,Course,Instructor,Chatlog
from django.core.mail import send_mail,EmailMessage
import razorpay
from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
from django.conf import settings
import google.generativeai as genai
from django.template.loader import render_to_string
from weasyprint import HTML
from xhtml2pdf import pisa
from io import BytesIO
from django.http import HttpResponse
import re
from .forms import ContactForm

# Create your views here.


#HOME PAGE

def home(request):

    students = Registration.objects.all()
    courses = Course.objects.all()
    enrollments= Enrollment.objects.all()

    return render(request, 'app0/home.html', {'students': students, 'courses': courses,'enrollments': enrollments})



# EDIT STUDENT DETAILS 

def edit_student(request,student_id):

    student = get_object_or_404(Registration,id=student_id)

    if request.method == "POST":
        student.name = request.POST.get('name')
        student.email= request.POST.get('email')
        student.mobile=request.POST.get('mobile')
        if 'image' in request.FILES:
            student.image = request.FILES['image']

        student.save()

        return redirect('app0:home') # redirect back to home
    
    return render(request , 'app0/edit_student.html',{'student':student})



# DELETE STUDENT DETAILS

def delete_student(request,student_id):

    student = get_object_or_404(Registration,id=student_id)

    if request.method == "POST":
        student.delete()
        return redirect('app0:home')
    
    return render(request, 'app0/delete_student.html',{'student': student})



# ADD STUDENTS

def add_student(request):

    if request.method == "POST":
        name= request.POST.get("name")
        email= request.POST.get("email")
        mobile= request.POST.get("mobile")
        image = request.FILES.get("image")
        
        student = Registration(
            name = name,
            email=email,
            mobile=mobile,
            image=image
        )
        student.save()
        return redirect("app0:home")
    
        # creating new student object
    return  render(request,"app0/add_details.html")



# ENROLL STUDENTS

def enroll_student(request,student_id):
    student= get_object_or_404(Registration,id=student_id)

    if request.method == "POST":
        courseId=request.POST.get("CourseId")
        instructorId=request.POST.get("InstructorId")
        enr_date=request.POST.get("Enr_date")
        enr_status=request.POST.get("Enr_status")
    
        #here it picks the course id and instructor id from the form
        course = get_object_or_404(Course, id=courseId)
        instructor = get_object_or_404(Instructor, id=instructorId)

        new_enrollment= Enrollment(
            studentId=student,
            courseId=course,
            instructorId=instructor,
            enr_date=enr_date,
            enr_status=enr_status
        )
        new_enrollment.save()
        return redirect("app0:home")
    
    courses= Course.objects.all()
    instructors = Instructor.objects.all()
    return  render(request,"app0/enroll_student.html", {
        'student':student,
        'courses':courses,
        'instructors': instructors
    })




# GET COURSE DETAILS

def course_details(request,course_id):

    course= get_object_or_404(Course,id=course_id)
    enrollments = Enrollment.objects.filter(courseId=course_id)

    return render(request,'app0/course_details.html',{'course':course,'enrollment':enrollments})



# GET INSTRUCTOR DETAILS

def instructor_details(request,inst_id):

    instructor = get_object_or_404(Instructor,id=inst_id)
    enrollments = Enrollment.objects.filter(instructorId=inst_id)

    return render(request,'app0/instructor_details.html',{'instructor':instructor,'enrollment':enrollments})



# ABOUT PAGE 

def about(request):

    students = Registration.objects.count()
    instructor = Instructor.objects.all()

    return render(request,'app0/about.html',{'instructors':instructor,'students':students})



# CONTACT PAGE

# def contact(request):

#     # send email

#     if request.method == "POST":
#         sender_name = request.POST.get("name")
#         sender_email= request.POST.get("email")
#         message = request.POST.get("message")

#         send_mail(
#             subject=f"{sender_name} sent a mail",
#             message=message,
#             from_email='testing142701@gmail.com',
#             recipient_list=['sharmasoham1427@gmail.com'],
#             fail_silently=False)
        
#         return redirect("app0:contact")
    
#     return render(request,"app0/contact.html")


def contact(request):
    # Initialize the contact form
    form = ContactForm()
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            # Extract data from the form
            # FIXED: Use form.cleaned_data to access form data
            sender_name = form.cleaned_data["name"]
            sender_email = form.cleaned_data["email"]
            message = form.cleaned_data["message"]

        # Step 1: Generate PDF
            students = Registration.objects.all()
            html = render_to_string("app0/get_student_pdf.html", {"students": students})
            pdf_result = BytesIO()
            pisa_status = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), pdf_result)

            if pisa_status.err:
                return HttpResponse("PDF generation failed", status=500)

        # Step 2: Compose and send email with PDF attachment
            email = EmailMessage(
                subject=f"{sender_name} sent a mail",
                body=message,
                from_email='testing142701@gmail.com',
                to=['sharmasoham1427@gmail.com']
            )

        # Attach PDF
            email.attach('student_report.pdf', pdf_result.getvalue(), 'application/pdf')

            email.send(fail_silently=False)

            return redirect("app0:contact")
        
    # If the request is GET , display the empty form
    # else:
        
    #     form = ContactForm()

    return render(request, "app0/contact.html",{"form": form })


def chat_bot_prompt(request):
    # client = genai.Client(api_key=settings.GEMINI_API_KEY)
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")  # or "gemini-pro"

    

    if request.method == "POST":
        prompt = request.POST.get("message")

        response_obj = model.generate_content(prompt)
        

        response_text = response_obj.text
    
        chat = Chatlog(
            prompt=prompt,
            response=response_text  # Now saving the actual text string
        )
        chat.save()

        return redirect('app0:chat_bot_response', chat_id=chat.id)
    return render(request, 'app0/chat_bot_prompt.html')



def chat_bot_response(request,chat_id):
    chat=get_object_or_404(Chatlog,id=chat_id)
    return render(request,"app0/chat_bot_response.html",{"chat":chat})




# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# def initiate_payment(request):
#     amount = 50000  # Amount in paise (₹500)
#     currency = 'INR'
#     receipt = 'order_rcptid_11'

#     razorpay_order = razorpay_client.order.create(dict(
#         amount=amount,
#         currency=currency,
#         receipt=receipt,
#         payment_capture=1
#     ))

#     context = {
#         'order_id': razorpay_order['id'],
#         'amount': amount,
#         'razorpay_key_id': settings.RAZORPAY_KEY_ID,
#         'currency': currency
#     }
#     return render(request, 'app0/payment_page.html', context)
def initiate_payment(request):
    amount = 50000  # Amount in paise (₹500)
    currency = 'INR'
    receipt = 'order_rcptid_11'

    razorpay_order = razorpay_client.order.create(dict(
        amount=amount,
        currency=currency,
        receipt=receipt,
        payment_capture=1
    ))

    context = {
        'order_id': razorpay_order['id'],
        'amount': amount / 100,  # Amount in rupees for display
        'amount_in_paise': amount,  # Amount in paise for Razorpay
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'currency': currency
    }
    return render(request, 'app0/payment_page.html', context)

@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        try:
            # Extract POST data
            razorpay_payment_id = request.POST.get('razorpay_payment_id')
            razorpay_order_id = request.POST.get('razorpay_order_id')
            razorpay_signature = request.POST.get('razorpay_signature')

            # Verify signature
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }

            razorpay_client.utility.verify_payment_signature(params_dict)
            return render(request, 'app0/success.html')

        except razorpay.errors.SignatureVerificationError:
            return HttpResponseBadRequest("Payment signature verification failed.")

    return HttpResponseBadRequest("Invalid request")







# def get_student_pdf(request):
#     students= Registration.objects.all()
#     html_string=render_to_string("app0/get_student_pdf.html",{'students':students})
#     html = HTML(string=html_string)
#     pdf= html.write_pdf()
#     response = HttpResponse(pdf, content_type='application/pdf')
#     response['Content-Disposition'] = 'attachment; filename="report.pdf"'
#     return response


def get_student_pdf(request):
    students = Registration.objects.all()
    html = render_to_string("app0/get_student_pdf.html", {"students": students})

    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    else:
        return HttpResponse("Error generating PDF", status=500)



# def get_student_pdf(request):
#     students = Registration.objects.all()

#     # Render HTML string from template
#     html_string = render_to_string("app0/get_student_pdf.html", {'students': students})

#     # Convert HTML to PDF (include base_url for resolving static files if needed)
#     html = HTML(string=html_string, base_url=request.build_absolute_uri())
#     pdf = html.write_pdf()

#     # Create response
#     response = HttpResponse(pdf, content_type='application/pdf')
#     response['Content-Disposition'] = 'attachment; filename="report.pdf"'

#     return response





from django.http import JsonResponse

def say_hello(request):
    return JsonResponse({'message':'hello soham'})

def hello_page(request):
    return render(request, 'app0/hello.html')
