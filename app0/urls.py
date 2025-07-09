from django.urls import path
from . import views
app_name='app0'
urlpatterns=[
    path('',views.home,name="home"),


    path('home/',views.home,name="home"),
    # jab yeh url pattern dikhega,tab yeh view call karna hai
    path('student/edit/<int:student_id>/',views.edit_student,name="edit_student"),
    path('student/delete/<int:student_id>/',views.delete_student,name="delete_student"),
    path('student/add/',views.add_student,name="add_student"),

    path('course/details/<int:course_id>/',views.course_details,name="course_details"),
    path('instructor/details/<int:inst_id>/',views.instructor_details,name="instructor_details"),

    path('student/enroll/<int:student_id>/',views.enroll_student,name="enroll_student"),

    path('contact/',views.contact,name="contact"),
    path('about/',views.about,name='about'),

    path('chat_bot/prompt',views.chat_bot_prompt,name="chat_bot_prompt"),
    path('chat_bot/response/<int:chat_id>/',views.chat_bot_response,name="chat_bot_response"),

    path('pay/', views.initiate_payment, name='initiate_payment'),
    path('payment/success/', views.payment_success, name='payment_success'),

    path("get_student_pdf/",views.get_student_pdf,name="get_student_pdf"),

    path('say-hello/', views.say_hello, name='say_hello'),
    path('hello-page/', views.hello_page, name='hello_page'),
    
]
