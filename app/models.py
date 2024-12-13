from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Teacher(models.Model):
    t_user=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    phone=models.CharField(max_length=255,null=True)
    address=models.CharField(max_length=255,null=True)
    image=models.ImageField(upload_to='images',null=True)
    status = models.CharField(max_length=20, default='Pending')

class Student(models.Model):
    s_user=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    phone=models.CharField(max_length=255,null=True)
    address=models.CharField(max_length=255,null=True)
    image=models.ImageField(upload_to='images',null=True)
    status = models.CharField(max_length=20, default='Pending')
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True) 

class Course(models.Model):
    coursename=models.CharField(max_length=255)
    duration=models.CharField(max_length=100)  
    startdate=models.DateField()
    fees=models.IntegerField(null=True)

class EnrollmentStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

class EnrollmentTeacher(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE,null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE,null=True)
    date = models.DateTimeField(auto_now_add=True)

class Attendance(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    date = models.DateField(null=True) 
    status = models.CharField(max_length=10, null=True)

class Assignment(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True)  
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    question = models.TextField(null=True)  
    start_date = models.DateField(null=True)  
    end_date = models.DateField(null=True)  
    pdf_file = models.FileField(upload_to='assignments/',null=True)
    status = models.CharField(max_length=20, default='Pending')
    submitted_at = models.DateTimeField(null=True, blank=True)
    assignment_verified = models.CharField(max_length=20, default='Not Verified')   
    late_days = models.IntegerField(default=0)

class Syllabus(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    pdf_file = models.FileField(upload_to='syllabus_pdfs/', null=True, blank=True)