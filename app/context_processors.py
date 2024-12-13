from .models import EnrollmentStudent

def course_count(request):
    if request.user.is_authenticated:
        count = EnrollmentStudent.objects.filter(student__status='Accepted').count()
        return {'course_count': count}
    return {'course_count': 0}
