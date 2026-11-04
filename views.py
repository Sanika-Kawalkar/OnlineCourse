 from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Course, Lesson, Question, Choice, Submission, Enrollment

# Other views (e.g., CourseListView, CourseDetailView, etc.) remain here...

def submit(request, course_id):
    # 1. Get the course object
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    # 2. Extract selected choice IDs from POST request
    selected_ids = request.POST.getlist('choice')

    # 3. Get or create the enrollment for the current user and course
    enrollment = Enrollment.objects.get(user=user, course=course)

    # 4. Create a new Submission instance for this enrollment
    submission = Submission.objects.create(enrollment=enrollment)

    # 5. Add selected choices to the submission's ManyToMany field
    if selected_ids:
        choices = Choice.objects.filter(id__in=selected_ids)
        submission.choices.set(choices)

    # 6. Redirect to show_exam_result with course_id and submission_id
    return HttpResponseRedirect(reverse('onlinecourse:show_exam_result', args=(course.id, submission.id)))


def show_exam_result(request, course_id, submission_id):
    # 1. Get course and submission objects
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)

    # 2. Extract selected choice IDs from the submission
    selected_ids = submission.choices.values_list('id', flat=True)

    # 3. Calculate the score and total possible grade
    total_score = 0
    total_possible = 0

    for question in course.question_set.all():
        total_possible += question.grade
        if question.is_get_score(selected_ids):
            total_score += question.grade

    # Calculate final grade percentage (or numerical score depending on template requirement)
    grade = int((total_score / total_possible) * 100) if total_possible > 0 else 0

    # 4. Pass required context variables to the result template
    context = {
        'course': course,
        'submission': submission,
        'selected_ids': selected_ids,
        'grade': grade,
    }

    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)
