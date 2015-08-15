from django.shortcuts import render, get_object_or_404, render_to_response

# Create your views here.
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone

from .models import Question, Choice

"""
def index(request):
	latest_question_list = Question.objects.order_by('-pub_date')[:5]
	template = loader.get_template('polls/index.html')
	context = RequestContext(request, {
		'latest_question_list': latest_question_list,
	})
	return HttpResponse(template.render(context))
	#OR
	#context = {'latest_question_list': latest_question_list}
	#return render(request, 'polls/index.html', context)
	
def detail(request, question_id):
	#return HttpResponse("You're looking at question %s." % question_id)
	try:
		question = Question.objects.get(pk=question_id)
	except Question.DoesNotExist:
		raise Http404("Question does not exist")
	return render(request, 'polls/detail.html', {'question': question})
	#OR
	#question = get_object_or_404(Question, pk=question_id)
	#return render(request, 'polls/detail.html', {'question': question})

def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/results.html', {'question': question})
"""
def vote(request, question_id):
	p = get_object_or_404(Question, pk=question_id)
	try:
		selected_choice = p.choice_set.get(pk=request.POST['choice'])
	except (KeyError, Choice.DoesNotExist):
		# Redisplay the question voting form.
		return render(request, 'polls/detail.html', {
			'question': p,
			'error_message': "You didn't select a choice.",
		})
	else:
		selected_choice.votes += 1
		selected_choice.save()
		# Always return an HttpResponseRedirect after successfully dealing
		# with POST data. This prevents data from being posted twice if a
		# user hits the Back button.
		return HttpResponseRedirect(reverse('polls:results', args=(p.id,)))

class IndexView(generic.ListView):
	template_name = 'polls/index.html'
	context_object_name = 'latest_question_list'
	
	#votes = [sum([choice.votes for choice in question.choice_set.all()]) for question in Question.objects.all()]
	#print(votes)
	
	#def get_queryset(self):
	#	"""Return the last five published questions."""
	#	return Question.objects.order_by('-pub_date')[:5]
	def get_queryset(self, order='-pub_date'):
		"""
		Return the last five published questions (not including those set to be
		published in the future).
		
		return Question.objects.filter(
			pub_date__lte=timezone.now()
		).order_by('-pub_date')[:5]
		"""
		ques = Question.objects.filter(
			pub_date__lte=timezone.now()
		).order_by('-pub_date', order)[:5]
		self.questions = []
		for i in ques:
			t = (i, sum([c.votes for c in i.choice_set.all()]), )
			self.questions.append(t)
		return ques
	
	def get(self, request, *args, **kwargs):
		#self.votes = [sum([choice.votes for choice in question.choice_set.all]) for question in Question.objects.all()]
		#print(self.votes)
		context = locals()
		order = request.GET.get('order_by', 'question_text')
		if order != "votes":
			self.get_queryset(order)
		else:
			self.get_queryset()
			self.questions.sort(key=lambda x: x[1])
		context['latest_question_list'] = self.questions
		#context['votes'] = self.votes
		return render_to_response(self.template_name, context, context_instance=RequestContext(request))


class DetailView(generic.DetailView):
	model = Question
	template_name = 'polls/detail.html'

class ResultsView(generic.DetailView):
	model = Question
	template_name = 'polls/results.html'
