from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, Question, Choice, Submission

def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    
    if request.method == 'POST':
        selected_ids = []
        for key, value in request.POST.items():
            if key.startswith('choice_'):
                selected_ids.append(int(value))
        
        submission = Submission.objects.create(user=user)
        selected_choices = Choice.objects.filter(id__in=selected_ids)
        submission.choices.set(selected_choices)
        submission.save()
        
        return redirect('onlinecourse:show_exam_result', course_id=course.id, submission_id=submission.id)

def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    selected_ids = submission.choices.values_list('id', flat=True)
    
    total_score = 0
    max_score = 0
    
    for question in course.question_set.all():
        max_score += question.grade
        if question.is_get_score(selected_ids):
            total_score += question.grade
            
    grade = (total_score / max_score) * 100 if max_score > 0 else 0
    
    context = {
        'course': course,
        'selected_ids': selected_ids,
        'total_score': total_score,
        'max_score': max_score,
        'grade': grade,
        'submission': submission
    }
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)
