from django.db import models

# Create your models here.

class Registration(models.Model):
    image= models.ImageField(upload_to='images/', default='images/default.jpg')
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15, unique=True)
    
    # Define the unique constraint for name and email
    def __str__(self):
        return f"{self.name} - {self.email}"






class Course(models.Model):
    course_name= models.CharField(max_length=100,unique=True)
    credit = models.IntegerField()
    course_code= models.CharField(max_length = 10,default="No code")
    course_description= models.TextField(blank=True)

    # Define the unique constraint for course_name
    def __str__(self):
        return f"{self.course_name} credit: {self.credit}"








class Instructor(models.Model):
    name = models.CharField(max_length=100)
    instructor_id=models.IntegerField()
    instructor_email=models.EmailField(default="nothing@gmail.com")
    instructor_phone= models.CharField(max_length=9,default="777777777")
    experience = models.IntegerField(default=0)
    # Define the unique constraint for instructor_id
    def __str__(self):
        return f"{self.instructor_id}:{self.name}"








class Enrollment(models.Model):
    studentId=models.ForeignKey(Registration, models.CASCADE)
    courseId=models.ForeignKey(Course, models.CASCADE)
    instructorId=models.ForeignKey(Instructor, models.CASCADE)
    enr_date=models.DateField()
    enr_status=models.BooleanField(default=True)

    def __str__(self):
        return f"Student: {self.studentId.name}, Course: {self.courseId.course_name}, Instructor: {self.instructorId.name}, Status: {'Enrolled' if self.enr_status else 'Not Enrolled'}"
    



class Chatlog(models.Model):
    prompt=models.TextField()
    response=models.TextField()