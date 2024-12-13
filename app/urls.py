from django.urls import path,include
from .import views

urlpatterns = [
    path('', views.homepage, name='homepage'),  
    path('loginpage',views.loginpage,name='loginpage'),
    path('logout',views.logout,name='logout'),
    path('signuppage',views.signuppage,name='signuppage'),
    path('usercreate',views.usercreate,name='usercreate'),
    path('userlog',views.userlog,name='userlog'),
    path('adminhome',views.adminhome,name='adminhome'),
    path('managestudent',views.managestudent,name='managestudent'),
    path('approvestudent', views.approvestudent, name='approvestudent'),
    path('acceptstudent/<int:acptstd>/', views.acceptstudent, name='acceptstudent'),
    path('rejectstudent/<int:rjctstd>/', views.rejectstudent, name='rejectstudent'),
    path('viewstudent', views.viewstudent, name='viewstudent'),
    path('deletestudent/<int:sd>',views.deletestudent,name='deletestudent'),
    path('assigncourse', views.assigncourse, name='assigncourse'),
    path('manageteacher',views.manageteacher,name='manageteacher'),
    path('approveteacher', views.approveteacher, name='approveteacher'),
    path('acceptteacher/<int:acpttchr>/', views.acceptteacher, name='acceptteacher'),
    path('rejectteacher/<int:rjcttchr>/', views.rejectteacher, name='rejectteacher'),
    path('teacherassigncourse', views.teacherassigncourse, name='teacherassigncourse'),
    path('viewteacher', views.viewteacher, name='viewteacher'),
    path('deleteteacher/<int:td>',views.deleteteacher,name='deleteteacher'),
    path('managecourse',views.managecourse,name='managecourse'),
    path('courseadd', views.courseadd, name='courseadd'),
    path('addcourse', views.addcourse, name='addcourse'),
    path('showcourse', views.showcourse, name='showcourse'),
    path('editcourse/<int:pc>',views.editcourse,name='editcourse'),
    path('updatecourse/<int:uc>',views.updatecourse,name='updatecourse'),
    path('deletecourse/<int:cd>',views.deletecourse,name='deletecourse'),
    path('addteacherattendance', views.addteacherattendance, name='addteacherattendance'),
    path('fetch-courses/<int:teacher_id>/', views.fetch_courses, name='fetch_courses'),
    path('viewteacherattendance/', views.viewteacherattendance, name='viewteacherattendance'),
    path('studenthome',views.studenthome,name='studenthome'),
    path('resetpassword',views.resetpassword,name='resetpassword'),
    path('passwordreset',views.passwordreset,name='passwordreset'),
    path('studentprofile/<int:sp>/', views.studentprofile, name='studentprofile'),
    path('studentprofileedit/<int:se>',views.studentprofileedit,name='studentprofileedit'),
    path('updatestudent/<int:us>/', views.updatestudent, name='updatestudent'),
    path('viewstudentattendance', views.viewstudentattendance, name='viewstudentattendance'),
    path('teacherhome',views.teacherhome,name='teacherhome'),
    path('resetpasswordteacher',views.resetpasswordteacher,name='resetpasswordteacher'),
    path('passwordresetteacher',views.passwordresetteacher,name='passwordresetteacher'),
    path('teacherprofile/<int:tp>/', views.teacherprofile, name='teacherprofile'),
    path('teacherprofileedit/<int:te>',views.teacherprofileedit,name='teacherprofileedit'),
    path('updateteacher/<int:ut>/', views.updateteacher, name='updateteacher'),
    path('addstudentattendance',views.addstudentattendance,name='addstudentattendance'),
    path('viewstudentforteacher', views.viewstudentforteacher, name='viewstudentforteacher'),
    path('viewcoursesforstudent', views.viewcoursesforstudent, name='viewcoursesforstudent'),
    path('viewcoursesforteacher', views.viewcoursesforteacher, name='viewcoursesforteacher'),
    # path('assignteacher', views.assignteacher, name='assignteacher'),
    # path('fetch-courses/<int:teacher_id>/', views.fetchcourses, name='fetch_courses'),  
    path('add_assignment/', views.add_assignment, name='add_assignment'),
    path('assignments/', views.student_assignments, name='student_assignments'),
    path('view_submitted_assignments/', views.view_submitted_assignments, name='view_submitted_assignments'),
    path('verify_assignment/<int:assignment_id>/', views.verify_assignment, name='verify_assignment'),
    path('delete-assignment/<int:assignment_id>/', views.delete_assignment, name='delete_assignment'),
    path('error/', views.error_page, name='some_error_page'),
    path('viewstudentattendancebyadmin', views.viewstudentattendancebyadmin, name='viewstudentattendancebyadmin'),
    path('viewteacherattendancebyadmin/', views.viewteacherattendancebyadmin, name='viewteacherattendancebyadmin'),
    path('moreaboutcourses', views.moreaboutcourses, name='moreaboutcourses'),
    path('viewstudentattendancebyteacher/', views.viewstudentattendancebyteacher, name='viewstudentattendancebyteacher'),
    path('viewsubmittedassignmentsbystudent', views.viewsubmittedassignmentsbystudent, name='viewsubmittedassignmentsbystudent'),
    path('assign_teacher_course_to_student/', views.assign_teacher_course_to_student, name='assign_teacher_course_to_student'),
    path('get-teachers-by-course/', views.get_teachers_by_course, name='get_teachers_by_course'),
    path('add-syllabus', views.add_syllabus, name='add_syllabus'),


]