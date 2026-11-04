
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import (
    Course,
    Question,
    Choice,
    Submission,
    Enrollment
)


@login_required
def submit(request, course_id):

    course = get_object_or_404(Course, pk=course_id)

    # Retrieve the current learner's enrollment
    enrollment = get_object_or_404(
        Enrollment,
        user=request.user,
        course=course,
        is_active=True
    )

    if request.method == 'POST':

        selected_ids = []

        for key, value in request.POST.items():

            if key.startswith('choice_'):
                try:
                    selected_ids.append(int(value))
                except (ValueError, TypeError):
                    continue

        submission = Submission.objects.create(
            enrollment=enrollment
        )

        selected_choices = Choice.objects.filter(
            id__in=selected_ids,
            question__course=course
        )

        submission.choices.set(selected_choices)

        return redirect(
            'onlinecourse:show_exam_result',
            course_id=course.id,
            submission_id=submission.id
        )

    return redirect(
        'onlinecourse:course_details',
        pk=course.id
    )


@login_required
def show_exam_result(request, course_id, submission_id):

    course = get_object_or_404(Course, pk=course_id)

    submission = get_object_or_404(
        Submission,
        pk=submission_id,
        enrollment__user=request.user,
        enrollment__course=course
    )

    selected_ids = list(
        submission.choices.values_list('id', flat=True)
    )

    questions = Question.objects.filter(course=course)

    total_score = 0
    max_score = 0
    exam_results = []

    for question in questions:

        max_score += question.grade

        is_correct = question.is_get_score(selected_ids)

        if is_correct:
            total_score += question.grade

        exam_results.append({
            'question': question,
            'is_correct': is_correct,
            'selected_choices': question.choice_set.filter(
                id__in=selected_ids
            ),
            'correct_choices': question.choice_set.filter(
                is_correct=True
            )
        })

    percentage = (
        round((total_score / max_score) * 100, 2)
        if max_score > 0 else 0
    )

    passed = percentage >= 70

    context = {
        'course': course,
        'submission': submission,
        'exam_results': exam_results,
        'total_score': total_score,
        'max_score': max_score,
        'grade': percentage,
        'percentage': percentage,
        'passed': passed,
    }

    return render(
        request,
        'onlinecourse/exam_result_bootstrap.html',
        context
    )
