from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Question, Choice, Submission


@login_required
def submit(request):
    if request.method == "POST":
        questions = Question.objects.all()
        score = 0
        total_questions = questions.count()

        for question in questions:
            selected_choice_id = request.POST.get(
                f"question_{question.id}"
            )

            if selected_choice_id:
                selected_choice = get_object_or_404(
                    Choice,
                    id=selected_choice_id,
                    question=question
                )

                Submission.objects.create(
                    student=request.user,
                    question=question,
                    selected_choice=selected_choice
                )

                if selected_choice.is_correct:
                    score += question.marks

        request.session["exam_score"] = score
        request.session["total_questions"] = total_questions

        return redirect("show_exam_result")

    return redirect("show_exam")


@login_required
def show_exam_result(request):
    score = request.session.get("exam_score", 0)
    total_questions = request.session.get("total_questions", 0)

    context = {
        "score": score,
        "total_questions": total_questions,
    }

    return render(request, "exam_result.html", context)
