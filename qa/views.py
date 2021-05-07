from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views import View
from django.urls import reverse
from django.views.generic import ListView
from django.http import HttpResponseRedirect, request
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from django.utils.decorators import method_decorator

from .models import Question, Answer, QuestionVote
from user_profile.models import ReputationHistory
from .privilages import Privilages
from .reputations import Reputation
from .mixins import PrivilageRequiredMixin


class QuestionList(ListView):
    queryset = Question.objects.all().prefetch_related('user', 'answer_set')
    context_object_name = 'questions'
    paginate_by = 10
    template_name = 'qa/index.html'


@method_decorator(login_required, name='dispatch')
class Ask(PrivilageRequiredMixin, View):
    privilage_required = 'create_post'

    def get(self, request):
        return render(request, 'qa/ask_question.html')

    def post(self, request):
        question = Question.objects.create(user=self.request.user,
                                           title=request.POST['title'],
                                           body_md=request.POST['body_md'])
        messages.add_message(request, messages.INFO,
                             _('Your question saved.'))
        return HttpResponseRedirect(reverse("qa:show",
                                            kwargs={
                                                "id": question.pk,
                                                "slug": question.slug
                                            }))


@method_decorator(login_required, name='dispatch')
class EditQuestion(View):

    def get(self, request, question_id):
        q = get_object_or_404(Question, pk=question_id)
        return render(request, 'qa/edit_question.html',
                      {'question': q})

    def post(self, request, question_id):
        q = get_object_or_404(Question, pk=question_id)
        try:
            if request.POST['title']:
                q.title = request.POST['title']
            if request.POST['body_md']:
                q.body_md = request.POST['body_md']
            q.save()
            messages.add_message(request, messages.INFO,
                                 _('Question updated'))
        except Exception as ex:
            messages.add_message(request, messages.WARNING,
                                 str(ex))
        return HttpResponseRedirect(reverse("qa:show",
                                            kwargs={
                                                'id': q.pk,
                                                'slug': q.slug
                                            }))


def show(request, id, slug):
    question = get_object_or_404(Question, pk=id, slug=slug)
    return render(request, 'qa/question.html', {'question': question})


@method_decorator(login_required, name='dispatch')
class AnswerQuestion(View):
    def post(self, request, id):
        q = get_object_or_404(Question, id=id)
        if request.POST['body_md']:
            Answer.objects.create(user=request.user,
                                  question=q,
                                  body_md=request.POST['body_md'])
            messages.add_message(request, messages.INFO,
                                 _('Your answer saved'))
        else:
            messages.add_message(request, messages.WARNING,
                                 _('Please enter your answer'))
        return HttpResponseRedirect(reverse("qa:show",
                                            kwargs={
                                                "id": q.pk,
                                                "slug": q.slug
                                            }))


@method_decorator(login_required, name='dispatch')
class QuestionVoteUp(PrivilageRequiredMixin, View):
    privilage_required = 'vote_up'

    def post(self, request, question_id):
        question = get_object_or_404(Question, pk=question_id)
        try:
            qv = QuestionVote.objects.create(
                user=request.user,
                question=question,
                rate=1)
            if qv:
                ReputationHistory.objects.create(
                    user=question.user,
                    cause=Reputation.QUESTION_VOTE_UP.name,
                    reputation=Reputation.QUESTION_VOTE_UP.value
                )
            return JsonResponse({
                'status': 'ok',
                'vote': Question.objects.get(pk=question_id).vote
            })
        except Exception as ex:
            return JsonResponse({
                'status': 'error',
                'error': str(ex)
            })


@method_decorator(login_required, name='dispatch')
class QuestionVoteDown(PrivilageRequiredMixin, View):
    privilage_required = 'vote_down'

    def post(self, request, question_id):
        question = get_object_or_404(Question, pk=question_id)
        try:
            qv = QuestionVote.objects.create(
                user=request.user,
                question=question,
                rate=-1)
            if qv:
                ReputationHistory.objects.create(
                    user=question.user,
                    cause=Reputation.QUESTION_VOTE_DOWN.name,
                    reputation=Reputation.QUESTION_VOTE_DOWN.value
                )
            return JsonResponse({
                'status': 'ok',
                'vote': Question.objects.get(pk=question_id).vote
            })
        except Exception as ex:
            return JsonResponse(
                {
                    'status': 'error',
                    'error': str(ex)
                })


@method_decorator(login_required, name='dispatch')
class EditAnswer(View):

    def get(self, request, question_id, answer_id):
        q = get_object_or_404(Question, pk=question_id)
        ans = get_object_or_404(Answer, pk=answer_id)
        return render(request, 'qa/edit_answer.html',
                      {'answer': ans, 'question': q})

    def post(self, request, question_id, answer_id):
        q = get_object_or_404(Question, pk=question_id)
        ans = get_object_or_404(Answer, pk=answer_id)
        try:
            if request.POST['body_md']:
                ans.body_md = request.POST['body_md']
                ans.save()
                messages.add_message(request, messages.INFO,
                                     _('Answer updated'))
        except Exception as ex:
            messages.add_message(request, messages.WARNING,
                                 str(ex))
        return HttpResponseRedirect(reverse("qa:show",
                                            kwargs={
                                                'id': q.pk,
                                                'slug': q.slug
                                            }))
