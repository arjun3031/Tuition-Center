from django.shortcuts import render,redirect,get_object_or_404
from app.models import *
from django.contrib.auth.models import User,auth
from django.contrib import messages
import os,re
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime



# Create your views here.
def homepage(request):
    return render(request,'homepage.html')


def loginpage(request):
    return render(request,'loginpage.html')

def logout(request):
    auth.logout(request)
    return redirect('homepage')

def signuppage(request):
    return render(request,'signuppage.html')

def usercreate(request):
    if request.method == 'POST':
        firstname = request.POST['fname']
        lastname = request.POST['lname']
        username = request.POST['uname']
        addresses = request.POST['address']
        mobile = request.POST['mobile']
        mail = request.POST['mail']
        img = request.FILES.get('img')
        role = request.POST['role']
        
        password = get_random_string(length=6)
        
        if username == mail:
            messages.info(request, 'Username and email cannot be the same')
            return redirect('signuppage')
    
        if User.objects.filter(username=username).exists():
            messages.info(request, 'Username already exists')
            return redirect('signuppage')
        
        # if User.objects.filter(email=mail).exists():
        #     messages.info(request, 'Email already exists')
        #     return redirect('signuppage')

        user = User.objects.create_user(first_name=firstname, last_name=lastname, email=mail, username=username)
        user.set_password(password) 
        user.save()

        if role == 'student':
            Student.objects.create(s_user=user, phone=mobile, address=addresses, image=img)
        elif role == 'teacher':
            Teacher.objects.create(t_user=user, phone=mobile, address=addresses, image=img)

        send_mail(
            'Your Account Password',
            f'Your password is: {password}',
            'arjunkmvat@gmail.com',
            [mail],
            fail_silently=False,
        )
        messages.success(request, 'Account created successfully! Please check your email for your password.')
        return redirect('signuppage')

    else:
        return render(request, 'signuppage.html')

def userlog(request):
    if request.method == 'POST':
        usname = request.POST['username']
        passwrd = request.POST['password']
        user = auth.authenticate(username=usname, password=passwrd)

        if user is not None:
            if user.is_staff:
                auth.login(request, user)
                return redirect('adminhome')  

            studentexists = Student.objects.filter(s_user=user).exists()
            if studentexists:
                student = Student.objects.get(s_user=user)
                if student.status != 'Accepted':
                    messages.info(request, 'Your account is not accepted yet.')
                    return redirect('loginpage')
                auth.login(request, user)
                messages.success(request, "New course is assigned on you!")
                return redirect('studenthome')

            teacherexists = Teacher.objects.filter(t_user=user).exists()
            if teacherexists:
                teacher = Teacher.objects.get(t_user=user)
                if teacher.status != 'Accepted':
                    messages.info(request, 'Your account is not accepted yet.')
                    return redirect('loginpage')
                auth.login(request, user)
                messages.success(request, "New course is assigned on you!")
                return redirect('teacherhome')

            messages.info(request, 'You do not have permission to login.')
            return redirect('loginpage')
        else:
            messages.info(request, 'Invalid username or password')
            return redirect('loginpage')
    else:
        return redirect('loginpage')

@login_required(login_url='homepage')
def adminhome(request):
    student_pending_count = Student.objects.filter(status='Pending').count()
    teacher_pending_count = Teacher.objects.filter(status='Pending').count()  
    return render(request, 'adminhome.html', {'student_pending_count': student_pending_count,'teacher_pending_count': teacher_pending_count})

@login_required(login_url='homepage')
def managestudent(request):
    count = Student.objects.filter(status='Pending').count() 
    teacher_pending_count = Teacher.objects.filter(status='Pending').count()  
    return render(request, 'managestudent.html', {'pending_count': count, 'teacher_pending_count': teacher_pending_count})

@login_required(login_url='homepage')
def approvestudent(request):
    pending=Student.objects.filter(status='Pending')
    student_pending_count = Student.objects.filter(status='Pending').count()
    teacher_pending_count = Teacher.objects.filter(status='Pending').count()  
    return render(request, 'approvestudent.html', {'pstudents': pending,'student_pending_count': student_pending_count,'teacher_pending_count': teacher_pending_count})

def acceptstudent(request, acptstd):
    student = Student.objects.get(id=acptstd)
    student.status = 'Accepted'
    student.save()    
    return redirect('approvestudent')

def rejectstudent(request, rjctstd):
    student = Student.objects.get(id=rjctstd)
    student.status = 'Rejected'
    student.save()    
    return redirect('approvestudent')

@login_required(login_url='homepage')
def viewstudent(request):
    teachers = Teacher.objects.all()
    courses = Course.objects.all()

    selected_teacher_id = request.GET.get('teacher')
    selected_course_id = request.GET.get('course')
    accepted_students = Student.objects.filter(status='Accepted').distinct()

    if selected_teacher_id:
        accepted_students = accepted_students.filter(
            enrollmentstudent__course__enrollmentteacher__teacher_id=selected_teacher_id
        ).distinct()
        selected_course_id = None 
    if selected_course_id and not selected_teacher_id:
        accepted_students = accepted_students.filter(
            enrollmentstudent__course_id=selected_course_id
        ).distinct()
        selected_teacher_id = None 

    return render(request, 'viewstudent.html', {
        'acceptedstudent': accepted_students,
        'teachers': teachers,
        'courses': courses,
        'selected_teacher': selected_teacher_id,
        'selected_course': selected_course_id,
        'student_pending_count': Student.objects.filter(status='Pending').count(),
        'teacher_pending_count': Teacher.objects.filter(status='Pending').count(),
    })

def deletestudent(request, sd):
    try:
        std = Student.objects.get(id=sd)        
        user = std.s_user        
        if user:
            user.delete()      
        std.delete()        
        messages.success(request, 'Student deleted successfully')
    except Student.DoesNotExist:
        messages.error(request, 'Student does not exist.')
    return redirect('viewstudent')

@login_required(login_url='homepage')
def assigncourse(request):
    students = Student.objects.filter(status='Accepted') 
    courses = Course.objects.all()  
    if request.method == 'POST':
        stud_id = request.POST.get('student') 
        crs_id = request.POST.get('course')    
        std = Student.objects.get(id=stud_id)
        cours = Course.objects.get(id=crs_id)
        if EnrollmentStudent.objects.filter(student=std, course=cours).exists():
            messages.error(request, "This student is already enrolled in the selected course")
        else:
            EnrollmentStudent.objects.create(student=std, course=cours)
            messages.success(request, "Course assigned successfully!")
        return redirect('teacherhome')
    return render(request, 'assigncourse.html', {'students': students, 'courses': courses})

@login_required(login_url='homepage')
def manageteacher(request):
    count = Teacher.objects.filter(status='Pending').count()  
    student_pending_count = Student.objects.filter(status='Pending').count()
    return render(request, 'manageteacher.html', {'pending_count': count,'student_pending_count': student_pending_count})

@login_required(login_url='homepage')
def approveteacher(request):
    pending=Teacher.objects.filter(status='Pending')
    student_pending_count = Student.objects.filter(status='Pending').count()
    teacher_pending_count = Teacher.objects.filter(status='Pending').count()  
    return render(request, 'approveteacher.html', {'pteachers': pending,'student_pending_count': student_pending_count,'teacher_pending_count': teacher_pending_count})

def acceptteacher(request, acpttchr):
    student = Teacher.objects.get(id=acpttchr)
    student.status = 'Accepted'
    student.save()    
    return redirect('approveteacher')

def rejectteacher(request, rjcttchr):
    student = Student.objects.get(id=rjcttchr)
    student.status = 'Rejected'
    student.save()    
    return redirect('approvestudent')

@login_required(login_url='homepage')
def viewteacher(request):
    courses = Course.objects.all()  
    selected_course_id = request.GET.get('course') 
    selected_course = None
    student_pending_count = Student.objects.filter(status='Pending').count()
    teacher_pending_count = Teacher.objects.filter(status='Pending').count()  
    if selected_course_id:
        selected_course = get_object_or_404(Course, id=selected_course_id)
        accepted_teachers = Teacher.objects.filter(
            status='Accepted', 
            enrollmentteacher__course=selected_course
        ).select_related('t_user').distinct()
    else:
        accepted_teachers = Teacher.objects.filter(status='Accepted').select_related('t_user').distinct()
    return render(request, 'viewteacher.html', {
        'acceptedteacher': accepted_teachers,
        'courses': courses,
        'selected_course': selected_course,
        'student_pending_count': student_pending_count,
        'teacher_pending_count': teacher_pending_count})

def deleteteacher(request, td):
    try:
        tchr = Teacher.objects.get(id=td)
        user = tchr.t_user  
        if user:
            user.delete()
        tchr.delete()
        messages.success(request, 'Teacher deleted successfully')
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher does not exist.')
    return redirect('viewteacher')

@login_required(login_url='homepage')
def teacherassigncourse(request):
    teachers = Teacher.objects.filter(status='Accepted').exclude(id__in=EnrollmentTeacher.objects.values_list('teacher_id', flat=True))
    courses = Course.objects.all()
    student_pending_count = Student.objects.filter(status='Pending').count()
    teacher_pending_count = Teacher.objects.filter(status='Pending').count()  
    if request.method == 'POST':
        crs_id = request.POST.get('course')
        tchr_id = request.POST.get('teacher')

        cours = Course.objects.get(id=crs_id)
        tchr = Teacher.objects.get(id=tchr_id)

        if EnrollmentTeacher.objects.filter(teacher=tchr).exists():
            messages.error(request, "This teacher is already enrolled in a course.")
        else:
            EnrollmentTeacher.objects.create(teacher=tchr, course=cours)
            messages.success(request, "Course assigned successfully!")
        return redirect('teacherassigncourse')
    return render(request, 'teachercourse.html', {'courses': courses, 'teachers': teachers,'student_pending_count': student_pending_count,'teacher_pending_count': teacher_pending_count})

@login_required(login_url='homepage')
def managecourse(request):
    student_pending_count = Student.objects.filter(status='Pending').count()
    teacher_pending_count = Teacher.objects.filter(status='Pending').count()  
    return render(request,'managecourse.html', {'student_pending_count': student_pending_count,'teacher_pending_count': teacher_pending_count})

@login_required(login_url='homepage')
def courseadd(request):
    student_pending_count = Student.objects.filter(status='Pending').count()
    teacher_pending_count = Teacher.objects.filter(status='Pending').count()  
    return render(request,'addcourse.html', {'student_pending_count': student_pending_count,'teacher_pending_count': teacher_pending_count})

def addcourse(request):
    if request.method=='POST':
        courses=request.POST['cname']
        fee=request.POST['fees']
        durations=request.POST['duration']
        strtdate=request.POST['startdate']
        c=Course(coursename=courses,fees=fee,duration=durations,startdate=strtdate)
        c.save()
        messages.info(request, 'New course added')
        return redirect('courseadd')

@login_required(login_url='homepage')
def showcourse(request):
    c=Course.objects.all()
    student_pending_count = Student.objects.filter(status='Pending').count()
    teacher_pending_count = Teacher.objects.filter(status='Pending').count()  
    return render(request, 'showcourses.html', {'c1':c,'student_pending_count': student_pending_count,'teacher_pending_count': teacher_pending_count})

def editcourse(request,pc):
    crs=Course.objects.get(id=pc)
    return render(request,'editcourse.html',{'crs1':crs})

def updatecourse(request,uc):
    if request.method=='POST':
        c=Course.objects.get(id=uc)
        c.coursename=request.POST.get('cname')
        c.fees=request.POST.get('fees')
        c.duration=request.POST.get('duration')
        c.startdate=request.POST.get('startdate')
        c.save()
        return redirect('showcourse')
    return render(request,'editcourse.html') 

def deletecourse(request, cd):
    crs=Course.objects.get(id=cd)
    crs.delete()
    return redirect('showcourse')

@login_required
def addteacherattendance(request):
    teachers = Teacher.objects.filter(status='Accepted')
    student_pending_count = Student.objects.filter(status='Pending').count()
    teacher_pending_count = Teacher.objects.filter(status='Pending').count()  
    if request.method == 'POST':
        teacher_id = request.POST.get('teacher')
        date = request.POST.get('date')
        status = request.POST.get('attendance')  
        course_id = request.POST.get('course_id')
        teacher = Teacher.objects.get(id=teacher_id)
        course = Course.objects.get(id=course_id) if course_id else None  
        Attendance.objects.create(teacher=teacher, date=date, status=status, course=course)  
        messages.success(request, "Attendance added successfully!")
        return redirect('addteacherattendance')  
    return render(request, 'addattendance.html', {'teachers': teachers,'student_pending_count': student_pending_count,'teacher_pending_count': teacher_pending_count})

def fetch_courses(request, teacher_id):
    courses = Course.objects.filter(enrollmentteacher__teacher_id=teacher_id).values('id', 'coursename')
    return JsonResponse({'courses': list(courses)})

def viewteacherattendance(request):
    teacher = Teacher.objects.get(t_user=request.user)
    attendance_records = Attendance.objects.filter(teacher=teacher)
    attendance_by_course = {}
    for record in attendance_records:
        course = record.course  
        if course not in attendance_by_course:
            attendance_by_course[course] = []
        attendance_by_course[course].append(record)
    context = {'teacher': teacher,'attendance': attendance_by_course}
    return render(request, 'viewteacherattendance.html', context)

@login_required(login_url='homepage')
def studenthome(request):
    student = Student.objects.get(s_user=request.user)
    return render(request,'studenthome.html',{'student': student})

@login_required
def resetpassword(request):
    return render(request,'resetpassword.html',{})

@login_required
def passwordreset(request):
    if request.method == 'POST':
        currentpassword= request.POST['cpassword']
        newpassword = request.POST['npassword']
        confirmpassword = request.POST['confirm']
        user = request.user
        if not user.check_password(currentpassword):
            messages.error(request, 'Current password is incorrect')
            return redirect('resetpassword')
        if newpassword != confirmpassword:
            messages.error(request, 'New password and confirm password do not match')
            return redirect('resetpassword')
        if len(newpassword) < 8 or not re.search(r'\d', newpassword) or not re.search(r'[@$!%*?&]', newpassword):
            messages.error(request, 'Require minimum 8 charectors, at least 1 digit and 1 special character')
            return redirect('resetpassword')
        user.set_password(newpassword)
        user.save()
        login(request, user)
        messages.success(request, 'Password reset successfully.')
        return redirect('resetpassword')  
    return render(request, 'resetpassword.html')

def studentprofile(request,sp):
    student=Student.objects.get(id=sp)
    courses = EnrollmentStudent.objects.filter(student=student).select_related('course')
    return render(request, 'studentprofile.html', {'student': student, 'courses': courses})

def studentprofileedit(request,se):
    student=Student.objects.get(id=se)
    user=student.s_user 
    return render(request,'studentprofileedit.html',{'std': user,'student':student})

def updatestudent(request, us):
    student = Student.objects.get(id=us)
    u = student.s_user  
    
    if request.method == 'POST':
        new_first_name = request.POST.get('fname')
        new_last_name = request.POST.get('lname')
        new_username = request.POST.get('uname')
        new_email = request.POST.get('mail')
        
        if User.objects.exclude(id=u.id).filter(username=new_username).exists():
            messages.error(request, "Username already exists.")
            return redirect('updatestudent', us=us)
        
        if User.objects.exclude(id=u.id).filter(email=new_email).exists():
            messages.error(request, "Email must be unique.")
            return redirect('updatestudent', us=us)
        
        if not re.match(r'.+\.com$', new_email):
            messages.error(request, "Email format is not correct")
            return redirect('updatestudent', us=us)
        
        u.first_name = new_first_name
        u.last_name = new_last_name
        u.username = new_username
        u.email = new_email
        u.save()
        student.phone = request.POST.get('phone')
        student.address = request.POST.get('address')
        new_img = request.FILES.get('image')  
        if new_img:
            if student.image and os.path.isfile(student.image.path):
                os.remove(student.image.path)
            student.image = new_img
        student.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('studentprofile', sp=student.id)
    return render(request, 'studentprofileedit.html', {'std': u, 'student': student})

@login_required(login_url='homepage')
def teacherhome(request):
    teacher = Teacher.objects.get(t_user=request.user)
    return render(request, 'teacherhome.html', {'teacher': teacher})

@login_required(login_url='login')
def resetpasswordteacher(request):
    teacher = Teacher.objects.get(t_user=request.user)
    return render(request,'resetpasswordteacher.html',{'teacher': teacher})

def passwordresetteacher(request):
    if request.method == 'POST':
        currentpassword= request.POST['cpassword']
        newpassword = request.POST['npassword']
        confirmpassword = request.POST['confirm']
        user = request.user
        if not user.check_password(currentpassword):
            messages.error(request, 'Current password is incorrect')
            return redirect('resetpasswordteacher')
        if newpassword != confirmpassword:
            messages.error(request, 'New password and confirm password do not match')
            return redirect('resetpasswordteacher')
        user.set_password(newpassword)
        user.save()
        
        login(request, user)
        messages.success(request, 'Password reset successfully.')
        return redirect('resetpasswordteacher')  
    return render(request, 'resetpasswordteacher.html')

def teacherprofile(request,tp):
    teacher=Teacher.objects.get(id=tp)
    courses = EnrollmentTeacher.objects.filter(teacher=teacher).select_related('course')
    return render(request, 'teacherprofile.html', {'teacher': teacher, 'courses': courses})

def teacherprofileedit(request,te):
    teacher=Teacher.objects.get(id=te)
    user=teacher.t_user 
    return render(request,'teacherprofileedit.html',{'tchr': user,'teacher':teacher})

def updateteacher(request, ut):
    teacher = Teacher.objects.get(id=ut)
    u = teacher.t_user  
    if request.method == 'POST':
        new_first_name = request.POST.get('fname')
        new_last_name = request.POST.get('lname')
        new_username = request.POST.get('uname')
        new_email = request.POST.get('mail')

        if User.objects.exclude(id=u.id).filter(username=new_username).exists():
            messages.error(request, "Username already exists.")
            return redirect('updateteacher', ut=ut)

        if User.objects.exclude(id=u.id).filter(email=new_email).exists():
            messages.error(request, "Email must be unique.")
            return redirect('updateteacher', ut=ut)
        u.first_name = new_first_name
        u.last_name = new_last_name
        u.username = new_username
        u.email = new_email
        u.save()
        teacher.phone = request.POST.get('phone')
        teacher.address = request.POST.get('address')

        new_img = request.FILES.get('image')
        if new_img:
            if teacher.image:
                if os.path.isfile(teacher.image.path):
                    os.remove(teacher.image.path)
            teacher.image = new_img
        teacher.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('teacherprofile', tp=teacher.id)
    return render(request, 'teacherprofileedit.html', {'tchr': u, 'teacher': teacher})

@login_required
def addstudentattendance(request):
    teacher = Teacher.objects.get(t_user=request.user) 
    students = Student.objects.filter(
        enrollmentstudent__course__in=EnrollmentTeacher.objects.filter(teacher=teacher).values('course'),status='Accepted').distinct()
    courses = Course.objects.filter(enrollmentteacher__teacher=teacher).distinct()
    
    if request.method == 'POST':
        student_id = request.POST.get('student')
        course_id = request.POST.get('course')
        attendance_status = request.POST.get('attendance') 
        date = request.POST.get('date')

        try:
            student = Student.objects.get(id=student_id)
            course = Course.objects.get(id=course_id)
            Attendance.objects.create(student=student, course=course, teacher=teacher, status=attendance_status, date=date)
            messages.success(request, "Attendance added successfully!")
        except Student.DoesNotExist:
            messages.error(request, "Student not found.")
        except Course.DoesNotExist:
            messages.error(request, "Course not found.")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

        return redirect('addstudentattendance')

    return render(request, 'addstudentattendance.html', {'students': students, 'courses': courses, 'teacher': teacher})

@login_required
def viewstudentattendance(request):
    student = Student.objects.get(s_user=request.user) 
    attendance_records = Attendance.objects.filter(student=student)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        attendance_records = attendance_records.filter(date__gte=start_date)
    if end_date:
        attendance_records = attendance_records.filter(date__lte=end_date)
    
    attendance_records = attendance_records.order_by('date')
    attendance_by_course = {}
    
    for record in attendance_records:
        course = record.course
        if course not in attendance_by_course:
            attendance_by_course[course] = []
        attendance_by_course[course].append(record)

    context = {
        'student': student,  
        'attendance': attendance_by_course,
    }
    
    return render(request, 'viewstudentattendance.html', context)


def viewstudentforteacher(request):
    try:
        teacher = Teacher.objects.get(t_user=request.user)  
    except Teacher.DoesNotExist:
        teacher = None 
    student_data = []
    if teacher:
        courses = Course.objects.filter(enrollmentteacher__teacher=teacher).distinct()
        for course in courses:
            enrollments = EnrollmentStudent.objects.filter(course=course).select_related('student')
            for enrollment in enrollments:
                assigned_teacher = EnrollmentTeacher.objects.filter(course=course).first()  
                student_data.append({'student': enrollment.student,'course': course,'assigned_teacher': assigned_teacher.teacher.t_user.first_name + " " + assigned_teacher.teacher.t_user.last_name if assigned_teacher else "N/A"})
    return render(request, 'viewstudentforteacher.html', {'student_data': student_data})

def viewcoursesforstudent(request):
    try:
        student = Student.objects.get(s_user=request.user)
        enrollments = EnrollmentStudent.objects.filter(student=student) \
            .select_related('course') \
            .prefetch_related('course__enrollmentteacher_set', 'course__syllabus_set')
    except Student.DoesNotExist:
        enrollments = []
    return render(request, 'viewcoursesforstudent.html', {'enrollments': enrollments})


def viewcoursesforteacher(request):
    try:
        teacher = Teacher.objects.get(t_user=request.user)
        enrollments = (EnrollmentTeacher.objects.filter(teacher=teacher).select_related('course').values('course').distinct())
        courses = Course.objects.filter(id__in=enrollments)
    except Teacher.DoesNotExist:
        courses = []  
    return render(request, 'viewcourseforteacher.html', {'courses': courses})

def assign_teacher_course_to_student(request):
    available_students = Student.objects.filter(status='Accepted', enrollmentstudent__isnull=True).distinct()
    courses = Course.objects.all()
    student_pending_count = Student.objects.filter(status='Pending').count()
    teacher_pending_count = Teacher.objects.filter(status='Pending').count()  
    
    if request.method == 'POST':
        student_id = request.POST.get('student')
        course_id = request.POST.get('course')
        teacher_id = request.POST.get('teacher')
        
        student = Student.objects.get(id=student_id)
        course = Course.objects.get(id=course_id)
        teacher = Teacher.objects.get(id=teacher_id)
        
        if EnrollmentStudent.objects.filter(student=student).exists():
            messages.error(request, "This student is already enrolled in a course.")
        else:
            EnrollmentStudent.objects.create(student=student, course=course)
            EnrollmentTeacher.objects.create(teacher=teacher, course=course)
            messages.success(request, "Teacher and course assigned to the student successfully!")
        return redirect('assign_teacher_course_to_student')
    return render(request, 'assignteacher(2).html', {'students': available_students, 'courses': courses,'student_pending_count': student_pending_count,'teacher_pending_count': teacher_pending_count})


def get_teachers_by_course(request):
    course_id = request.GET.get('course_id')
    if course_id:
        teachers = Teacher.objects.filter(enrollmentteacher__course_id=course_id).distinct()
        teacher_options = '<option value="">Select teacher</option>'
        for teacher in teachers:
            teacher_options += f'<option value="{teacher.id}">{teacher.t_user.first_name}&nbsp{teacher.t_user.last_name}</option>'
        return JsonResponse(teacher_options, safe=False)
    return JsonResponse({'error': 'Invalid course ID'}, status=400)

def viewteacherattendance(request):
    teacher = Teacher.objects.get(t_user=request.user)
    attendance_records = Attendance.objects.filter(teacher=teacher).order_by('date')
    courses = Course.objects.filter(enrollmentteacher__teacher=teacher).distinct()
    teacher_attendance_records = attendance_records.filter(student__isnull=True)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        teacher_attendance_records = teacher_attendance_records.filter(date__range=[start_date, end_date])
    context = {'teacher': teacher,'attendance': teacher_attendance_records,'courses': courses }
    return render(request, 'viewteacherattendance.html', context)

def add_assignment(request):
    teacher = get_object_or_404(Teacher, t_user=request.user) 
    if request.method == 'POST':
        student_id = request.POST.get('student')
        assignment_question = request.POST.get('assignment_question')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        student = get_object_or_404(Student, id=student_id) 
        if end_date < start_date:
            messages.error(request, "End date cannot be before start date.")
            return redirect('add_assignment')
        assignment = Assignment(teacher=teacher,student=student,question=assignment_question,start_date=start_date,end_date=end_date)
        assignment.save()
        messages.success(request, "Assignment successfully added!")
        return redirect('add_assignment')
    students = Student.objects.filter(enrollmentstudent__course__in=EnrollmentTeacher.objects.filter(teacher=teacher).values('course'),status='Accepted').distinct()

    context = {'students': students}
    return render(request, 'addassignment.html', context)

def student_assignments(request):
    student = get_object_or_404(Student, s_user=request.user)  
    assignments = Assignment.objects.filter(student=student, status='Pending').select_related('teacher')
    if request.method == "POST":
        assignment_id = request.POST.get('assignment_id')
        pdf_file = request.FILES.get('pdf_file')
        assignment = get_object_or_404(Assignment, id=assignment_id) 
        if pdf_file:
            assignment.pdf_file.save(pdf_file.name, pdf_file)
            assignment.status = 'Submitted'
            assignment.submitted_at = timezone.now()
            assignment.save()
            messages.success(request, 'Assignment submitted successfully!')
            assignments = assignments.exclude(id=assignment.id)
        else:
            messages.error(request, 'Please upload a valid PDF file.')

    context = {'student': student, 'assignments': assignments}
    return render(request, 'viewassignment.html', context)

def view_submitted_assignments(request):
    teacher = get_object_or_404(Teacher, t_user=request.user)
    assignments = Assignment.objects.filter(teacher=teacher)
    student_id = request.GET.get('student_id')
    assignment_question = request.GET.get('assignment_question')
    selected_student = None
    selected_question = None
    if student_id:
        selected_student = get_object_or_404(Student, id=student_id)
        assignments = assignments.filter(student=selected_student)
    if assignment_question:
        assignments = assignments.filter(question=assignment_question)
        selected_question = assignment_question
        if not student_id:
            assignments = Assignment.objects.filter(question=assignment_question)
    students = Student.objects.filter(enrollmentstudent__course__in=EnrollmentTeacher.objects.filter(teacher=teacher).values('course'),status='Accepted').distinct()
    assignment_questions = Assignment.objects.filter(teacher=teacher).values_list('question', flat=True).distinct()
    context = {'assignments': assignments,'students': students,'selected_student': selected_student.id if selected_student else None,'assignment_questions': assignment_questions,'selected_question': selected_question}
    return render(request, 'viewassignmentbyteacher.html', context)

def verify_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if assignment.status == 'Submitted' and assignment.assignment_verified == 'Not Verified':
        if assignment.submitted_at:
            if assignment.submitted_at.date() > assignment.end_date:
                late_days = (assignment.submitted_at.date() - assignment.end_date).days
                assignment.late_days = late_days 
                assignment.assignment_verified = 'Verified'
                assignment.save()
                messages.warning(request, f"Assignment verified but submitted {late_days} days late.")
            else:
                assignment.assignment_verified = 'Verified'
                assignment.late_days = 0 
                assignment.save()
                messages.success(request, "Assignment verified successfully.")
        else:
            messages.warning(request, "Cannot verify the assignment as it has not been submitted.")
    elif assignment.assignment_verified == 'Verified':
        if assignment.late_days > 0:
            messages.warning(request, f"This assignment was submitted {assignment.late_days} days late.")
        else:
            messages.info(request, "This assignment has already been verified.")
    return redirect('view_submitted_assignments')


def delete_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)  
    assignment.delete()
    messages.success(request, 'Assignment deleted successfully.')
    return redirect('view_submitted_assignments')

def viewsubmittedassignmentsbystudent(request):
    student = get_object_or_404(Student, s_user=request.user)
    filter_verified = request.GET.get('verified', None)
    assignments = Assignment.objects.filter(student=student, status='Submitted').select_related('teacher').order_by('-submitted_at')
    if filter_verified == 'verified':
        assignments = assignments.filter(assignment_verified='Verified')
    elif filter_verified == 'not_verified':
        assignments = assignments.filter(assignment_verified='Not Verified')
    for assignment in assignments:
        if assignment.submitted_at and assignment.submitted_at.date() > assignment.end_date:
            assignment.late_days = (assignment.submitted_at.date() - assignment.end_date).days
        else:
            assignment.late_days = 0 

    context = {
        'student': student,
        'assignments': assignments,
        'filter_verified': filter_verified
    }
    return render(request, 'viewsubmittedassignements.html', context)



def error_page(request):
    return render(request, 'error_page.html')

# @login_required(login_url='homepage')
# def viewstudentattendancebyadmin(request):
#     students = Student.objects.filter(status='Accepted')
#     teachers = Teacher.objects.filter(status='Accepted')
#     courses = Course.objects.all()
#     student_pending_count = Student.objects.filter(status='Pending').count()
#     teacher_pending_count = Teacher.objects.filter(status='Pending').count()  
#     selected_student = None
#     selected_teacher = None
#     selected_course = None
#     start_date = None
#     end_date = None
#     attendance_records = []

#     if request.method == 'GET':
#         student_id = request.GET.get('student_id')
#         teacher_id = request.GET.get('teacher_id')
#         course_id = request.GET.get('course_id')
#         start_date_str = request.GET.get('start_date')
#         end_date_str = request.GET.get('end_date')

#         if start_date_str:
#             start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
#         if end_date_str:
#             end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

#         if student_id:
#             selected_student = get_object_or_404(Student, id=student_id)
#         if teacher_id:
#             selected_teacher = get_object_or_404(Teacher, id=teacher_id)
#         if course_id:
#             selected_course = get_object_or_404(Course, id=course_id)

#         filters = {}
#         if selected_student:
#             filters['student'] = selected_student
#         if selected_teacher:
#             filters['teacher'] = selected_teacher
#         if selected_course:
#             filters['course'] = selected_course
#         if start_date:
#             filters['date__gte'] = start_date
#         if end_date:
#             filters['date__lte'] = end_date
#         attendance_records = Attendance.objects.filter(**filters).exclude(student=None)
#     context = {
#         'students': students,
#         'teachers': teachers,
#         'courses': courses,
#         'attendance': attendance_records,
#         'selected_student': selected_student,
#         'selected_teacher': selected_teacher,
#         'selected_course': selected_course,
#         'start_date': start_date,
#         'end_date': end_date,'student_pending_count': student_pending_count,'teacher_pending_count': teacher_pending_count}
#     return render(request, 'viewstudentattendancebyadmin.html', context)

@login_required(login_url='homepage')
def viewstudentattendancebyadmin(request):
    students = Student.objects.filter(status='Accepted')
    teachers = Teacher.objects.filter(status='Accepted')
    courses = Course.objects.all()
    student_pending_count = Student.objects.filter(status='Pending').count()
    teacher_pending_count = Teacher.objects.filter(status='Pending').count()  
    selected_student = None
    selected_teacher = None
    selected_course = None
    start_date = None
    end_date = None
    attendance_records = []

    if request.method == 'GET':
        student_id = request.GET.get('student_id')
        teacher_id = request.GET.get('teacher_id')
        course_id = request.GET.get('course_id')
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

        if student_id:
            selected_student = get_object_or_404(Student, id=student_id)
        if teacher_id:
            selected_teacher = get_object_or_404(Teacher, id=teacher_id)
        if course_id:
            selected_course = get_object_or_404(Course, id=course_id)

        filters = {}
        if selected_student:
            filters['student'] = selected_student
        if selected_teacher:
            filters['teacher'] = selected_teacher
        if selected_course:
            filters['course'] = selected_course
        if start_date:
            filters['date__gte'] = start_date
        if end_date:
            filters['date__lte'] = end_date

        if selected_student:
            attendance_records = Attendance.objects.filter(**filters).exclude(student=None)
        elif selected_course:
            attendance_records = Attendance.objects.filter(course=selected_course).exclude(student=None)
        else:
            attendance_records = Attendance.objects.exclude(student=None)

    context = {
        'students': students,
        'teachers': teachers,
        'courses': courses,
        'attendance': attendance_records,
        'selected_student': selected_student,
        'selected_teacher': selected_teacher,
        'selected_course': selected_course,
        'start_date': start_date,
        'end_date': end_date,
        'student_pending_count': student_pending_count,
        'teacher_pending_count': teacher_pending_count
    }
    return render(request, 'viewstudentattendancebyadmin.html', context)

def viewteacherattendancebyadmin(request):
    teachers = Teacher.objects.filter(status='Accepted')
    courses = Course.objects.all() 
    student_pending_count = Student.objects.filter(status='Pending').count()
    teacher_pending_count = Teacher.objects.filter(status='Pending').count()  
    selected_teacher = None
    selected_course = None
    start_date = None
    end_date = None
    attendance_records = {
        'teacher': {},
    }
    
    if request.method == 'GET':
        teacher_id = request.GET.get('teacher_id')
        start_date_str = request.GET.get('start_date') 
        end_date_str = request.GET.get('end_date')  
        
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        if teacher_id:
            selected_teacher = get_object_or_404(Teacher, id=teacher_id)

        filters = {}
        if selected_teacher:
            filters['teacher'] = selected_teacher
        if start_date:
            filters['date__gte'] = start_date 
        if end_date:
            filters['date__lte'] = end_date

        teacher_attendance_records = Attendance.objects.filter(**filters, student__isnull=True).order_by('date')
        
        for record in teacher_attendance_records:
            course = record.course  
            if course not in attendance_records['teacher']:
                attendance_records['teacher'][course] = []
            attendance_records['teacher'][course].append(record)

    if not selected_teacher:
        all_attendance_records = Attendance.objects.filter(student__isnull=True).order_by('date')
        for record in all_attendance_records:
            course = record.course  
            if course not in attendance_records['teacher']:
                attendance_records['teacher'][course] = []
            attendance_records['teacher'][course].append(record)

    context = {
        'teachers': teachers,
        'courses': courses,
        'attendance': attendance_records,
        'selected_teacher': selected_teacher,
        'selected_course': selected_course,
        'start_date': start_date,
        'end_date': end_date,
        'student_pending_count': student_pending_count,
        'teacher_pending_count': teacher_pending_count
    }
    
    return render(request, 'viewteacherattendancebyadmin.html', context)

def moreaboutcourses(request):
    return render(request,'moreaboutcourses.html')

def viewstudentattendancebyteacher(request):
    try:
        teacher = Teacher.objects.get(t_user=request.user)
        courses = EnrollmentTeacher.objects.filter(teacher=teacher).values_list('course', flat=True)
        students = Student.objects.filter(enrollmentstudent__course__in=courses).distinct()
        selected_student_id = request.GET.get('student')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        attendances = Attendance.objects.filter(teacher=teacher)
        if selected_student_id:
            attendances = attendances.filter(student_id=selected_student_id)
        if start_date:
            attendances = attendances.filter(date__gte=start_date)
        if end_date:
            attendances = attendances.filter(date__lte=end_date)
        attendances = attendances.order_by('date')
    except Teacher.DoesNotExist:
        students = []
        attendances = []
    return render(request, 'viewstudentattendancebyteacher.html',{'students': students,'attendances': attendances})

def add_syllabus(request):
    courses_with_syllabus = Syllabus.objects.values_list('course_id', flat=True)
    available_courses = Course.objects.exclude(id__in=courses_with_syllabus)
    student_pending_count = Student.objects.filter(status='Pending').count()
    teacher_pending_count = Teacher.objects.filter(status='Pending').count()  
    if request.method == 'POST':
        course_id = request.POST.get('course')
        syllabus_pdf = request.FILES.get('pdf_file')

        if not course_id or not syllabus_pdf:
            messages.error(request, "Please select a course and upload a syllabus.")
        else:
            try:
                course = Course.objects.get(id=course_id)
                Syllabus.objects.create(course=course, pdf_file=syllabus_pdf) 
                messages.success(request, f"Syllabus uploaded successfully for {course.coursename}!")
                return redirect('add_syllabus')
            except Course.DoesNotExist:
                messages.error(request, "The selected course does not exist.")
    return render(request, 'addsyllabus.html', {'courses': available_courses,'student_pending_count': student_pending_count,'teacher_pending_count': teacher_pending_count})






