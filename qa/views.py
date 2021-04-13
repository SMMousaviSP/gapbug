from django.shortcuts import get_object_or_404, render
from django.views import View
from django.urls import reverse
from django.views.generic import ListView
from django.http import HttpResponseRedirect
from .models import Question


class QuestionList(ListView):
    queryset = Question.objects.all()
    context_object_name = 'questions'
    paginate_by = 50
    template_name = 'qa/index.html'


class Ask(View):
    def get(self, request):
        return render(request, 'qa/ask_question.html')

    def post(self, request):
        question = Question.objects.create(user=self.request.user,
                                           title=request.POST['title'],
                                           body_md=request.POST['body_md'])

        return HttpResponseRedirect(reverse("qa:show",
                                            kwargs={
                                                "id": question.pk,
                                                "slug": question.slug
                                            }))


def show(request, id, slug):
    question = get_object_or_404(Question, pk=id, slug=slug)
    return render(request, 'qa/question.html', {'question': question})
