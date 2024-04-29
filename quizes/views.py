from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import MultipleObjectsReturned
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.forms import formset_factory
from django.db.models import Q
import json

from .models import Quiz, Question, Choice, Material, Topic
from .forms import CreateQuizForm, SingleQuestionForm, MaterialForm, CreateQuestionForm
from users.models import User

from django.core.servers.basehttp import WSGIServer
WSGIServer.handle_error = lambda *args, **kwargs: None

def index(request):
    all_quiz_list = Quiz.objects.all()
    context = {
        'all_quiz_list': all_quiz_list,
        'topics': Topic.objects.all(),
    }
    if request.method == "POST":
        data = request.POST.dict()
        quiz_title = data["name"] or ""
        topic = data["topic"] or ""
        url = reverse('quiz:search')+f"?name={quiz_title}&topic={topic}"
        return HttpResponseRedirect(url)
    return render(request, 'quiz/index.html', context)

def search(request):
    if request.method == "GET":
        data = request.GET.dict()
        quiz_title = data["name"] or ""
        topic = data["topic"] or ""
        all_quiz_list = Quiz.objects.filter(Q(quiz_title__contains=quiz_title) & Q(topic__contains=topic))
        context = {
            'all_quiz_list': all_quiz_list,
            'topics': Topic.objects.all(),
        }
    if request.method == "POST":
        data = request.POST.dict()
        quiz_title = data["name"] or ""
        topic = data["topic"] or ""
        url = reverse('quiz:search')+f"?name={quiz_title}&topic={topic}"
        HttpResponseRedirect(reverse('quiz:index'))
        return HttpResponseRedirect(url)
    return render(request, 'quiz/index.html', context)

def topic(request, topic):
    all_quiz_list = Quiz.objects.filter(topic=topic)
    context = {
        'all_quiz_list': all_quiz_list,
        'topics': Topic.objects.all(),
    }
    if request.method == "POST":
        HttpResponseRedirect(reverse('quiz:index'))
        return HttpResponseRedirect(reverse('quiz:search', args=([request.POST.get("search-field"),])))
    return render(request, 'quiz/search.html', context)

def single_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    num_questions = len(quiz.question_set.all())
    quiz_questions = Question.objects.filter(quiz=quiz)
    materials = quiz.material
    material = None
    if materials:
        material = Material.objects.get(id=materials)
    quiz.num_questions = num_questions
    quiz.save()
    request.session["questions"] = []
    request.session["q_num"] = 1
    request.session["num_correct"] = 0
    request.session["num_wrong"] = 0
    request.session["all_result"] = 0
    request.session["num_partially_true"] = 0
    quiz_question = None
    if quiz_questions.count():
        quiz_question = Question.objects.filter(quiz=quiz)[0]
        if request.POST:
            return HttpResponseRedirect(reverse('quiz:single_question', args=(quiz.id, quiz_question.id,)))
    context = {
        'userId': request.user.id,
        'current_question': quiz_question,
        'quiz': quiz,
        'quiz_questions': quiz_questions,
        'num_questions': num_questions,
        'user_creator': quiz.user_creator,
        'material': material,
        'url': request.build_absolute_uri(),
    }
    return render(request, 'quiz/single_quiz.html', context)

@login_required(login_url="users:login")
def single_question(request, quiz_id, question_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    question = Question.objects.filter(quiz=quiz, id=question_id).first()
    if request.method == "POST":
        form = SingleQuestionForm(data=request.POST, q_id=question_id)
        if not question.id in request.session["questions"]:
            question = Question.objects.filter(quiz=quiz, id=question_id).first()
            choises = Choice.objects.filter(question=question).all()
            correct_choises = Choice.objects.filter(question=question,correct_choise=True).all()
            user_choises = []
            fields = form.fields
            user_result = 0
            if form.is_valid():
                index = 0
                if "continue" in request.POST:
                    user_result = 0
                else:
                    for field in fields:
                        if field[:7] == "choise_":
                            if form.cleaned_data[field] and choises[index].correct_choise:
                                user_result += 1
                            elif form.cleaned_data[field] == False and choises[index].correct_choise == False: pass
                            else:
                                user_result -= 1/choises.count()
                            if form.cleaned_data[field]:
                                user_choises.append(field)
                            index += 1
                    if (not user_choises) and (not correct_choises):
                        user_result += 1
                if user_result > 1:
                    user_result = 1
                    request.session["num_correct"] += 1
                elif user_result < 0:
                    user_result = 0
                    request.session["num_wrong"] += 1
                    print("WRONG")
                else:
                    request.session["num_partially_true"] += 1
                request.session["all_result"] += user_result
                request.session["questions"].append(question.id)
        quiz_questions = list(Question.objects.filter(quiz=quiz))
        q_question_id = quiz_questions.index(Question.objects.get(id=question_id))

        if question != quiz_questions[-1]:
            next_question_id = quiz_questions[q_question_id+1].id
            request.session["q_num"] += 1
            return HttpResponseRedirect(reverse('quiz:single_question', args=(quiz.id, next_question_id,)))
        else:
            return HttpResponseRedirect(reverse('quiz:results', args=(quiz.id,)))
    else:
        form = SingleQuestionForm(q_id=question_id)
    context = {
        'q_num': request.session["q_num"],
        'current_question': question,
        "form": form,
        'quiz': quiz,
    }

    return render(request, 'quiz/single_question.html', context)

@login_required(login_url="users:login")
def results(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)

    num_correct = request.session["num_correct"]
    num_wrong = request.session["num_wrong"]
    num_partially_true = request.session["num_partially_true"]

    total_questions = Question.objects.filter(quiz=quiz).count()
    if num_correct > total_questions:
        num_correct = total_questions
    accuracy = num_correct/(total_questions)

    accuracy_over_75 = False
    if accuracy >= .75:
        accuracy_over_75 = True
    print(request.session["all_result"])
    accuracy_formatted = "{:.0%}".format(request.session["all_result"]/total_questions)

    context = {
        'num_correct': num_correct,
        'num_wrong': num_wrong,
        'num_partially_true': num_partially_true,
        'accuracy_over_75': accuracy_over_75,
        'accuracy_formatted': accuracy_formatted,
        'total_questions': total_questions,
        'quiz': quiz,
    }
    quiz_info = {
        'id': quiz.id,
        'quiz_title': quiz.quiz_title,
        'quiz_description': quiz.quiz_description,
        'topic': quiz.topic,
        'num_correct': str(num_correct),
        'num_wrong': str(num_wrong),
        'num_partially_true': str(num_partially_true),
        'total_questions': str(total_questions),
        'creator': quiz.user_creator
    }
    userModel = User.objects.get(id=request.user.id)
    completed_quizes = eval(str(request.user.completed_quizes))
    completed_quizes.append(quiz_info)
    userModel.completed_quizes = completed_quizes
    userModel.save()
    return render(request, 'quiz/results.html', context)

@login_required(login_url="users:login")
def create_quiz(request):
    if request.method == 'POST':
        form = CreateQuizForm(request.POST)
        if form.is_valid():
            quiz_name = form.cleaned_data['quiz_name']
            quiz_description = form.cleaned_data['quiz_description']
            material = form.cleaned_data['material']
            topic = form.cleaned_data['topic']
            user_info = {
                'id': request.user.id,
                'username': request.user.username,
            }
            new_quiz = Quiz(quiz_title=quiz_name, quiz_description=quiz_description, topic=topic, user_creator=user_info)
            if material:
                new_quiz.material = material.id
            new_quiz.save()
            quiz = Quiz.objects.get(pk=new_quiz.id)
            quiz_info = {
                'id': quiz.id,
                'quiz_title': quiz.quiz_title,
                'quiz_description': quiz.quiz_description,
                'topic': quiz.topic,
                'num_questions': quiz.num_questions or "0"
            }
            userModel = User.objects.get(id=request.user.id)
            created_quizes = eval(request.user.created_quizes)
            created_quizes.append(quiz_info)
            userModel.created_quizes = created_quizes
            userModel.save()
            return HttpResponseRedirect(reverse('quiz:create_question', args=(new_quiz.id, 1,)))
    else:
        form = CreateQuizForm()

    context = {
        'form': form,
    }

    return render(request, 'quiz/create_quiz.html', context)

@login_required(login_url="users:login")
def create_question(request, quiz_id, question_id):
    data = request.POST.dict()
    quiz = Quiz.objects.get(pk=quiz_id)
    if int(quiz.user_creator.get("id")) == int(request.user.id):
        if request.method == 'POST':
            form = CreateQuestionForm(data=request.POST)
            if form.is_valid():
                text = form.cleaned_data["question_text"]
                print(text)
            fields = list(data.keys())
            question = Question(quiz=quiz, question_text=str(text), question_num=question_id, timeout=data["timeout"])
            question.save()
            for choise in fields:
                if choise[:7] == "choise_" and (choise[-1] in "0123456789"):
                    try:
                        correctness = data[choise+"_correctness"]
                        if correctness == "" or correctness == "on":
                            correctness = True
                    except KeyError:
                        correctness = False
                    question.choice_set.create(question=question, text=data[choise], correct_choise=correctness)
            creator = User.objects.get(id=quiz.user_creator.get("id"))
            for i in eval(creator.created_quizes):
                if int(i.get("id")) == int(quiz.id):
                    i["num_questions"] = int(i["num_questions"]) + 1
                    creator.save()
            question.save()            
            if "continue" in request.POST:
                return HttpResponseRedirect(reverse('quiz:create_question', args=(quiz_id, question_id+1,)))
            else:
                return HttpResponseRedirect(reverse('quiz:single_quiz', args=(quiz_id,)))
        else:
            form = CreateQuestionForm()

        next_submit = "Далее"

        context = {
            'form': form,
            'question_num': question_id,
            'next_submit': next_submit,

        }

        return render(request, 'quiz/create_question.html', context=context)
    else:
        return HttpResponseRedirect(reverse('quiz:single_quiz', args=(quiz_id,)))


def create_material(request):
    if request.method == 'POST':
        form = MaterialForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('quiz:index'))
    else:
        form = MaterialForm()
        context = {
                'form':form
                }
            
    return render(request, 'quiz/create_material.html', context)

def single_material(request, mat_id):
    material = get_object_or_404(Material, pk=mat_id)
    context = {
        'material': material,
    }
    return render(request, 'quiz/single_material.html', context)

@login_required(login_url="users:login")
def edit_question(request, quiz_id, question_id):
    data = request.POST.dict()
    quiz = Quiz.objects.get(pk=quiz_id)
    question = Question.objects.filter(quiz=quiz, id=question_id)
    choices = Choice.objects.filter(question=question.first())
    if int(quiz.user_creator.get("id")) == int(request.user.id):
        if request.method == 'POST':
            form = CreateQuestionForm(data=request.POST, instance=question.first())
            if form.is_valid():
                text = form.cleaned_data["question_text"]
                print(text)
            fields = list(data.keys())
            question.update(quiz=quiz, question_text=str(text), question_num=question_id, timeout=data["timeout"])
            question.first().save()
            for oldchoise in choices:
                oldchoise.delete()
            for choise in fields:
                if choise[:7] == "choise_" and (choise[-1] in "0123456789"):
                    try:
                        correctness = data[choise+"_correctness"]
                        if correctness == "" or correctness == "on":
                            correctness = True
                    except KeyError:
                        correctness = False
                    question.first().choice_set.create(question=question.first(), text=data[choise], correct_choise=correctness)
            creator = User.objects.get(id=quiz.user_creator.get("id"))
            for i in eval(creator.created_quizes):
                if int(i.get("id")) == int(quiz.id):
                    i["num_questions"] = int(i["num_questions"]) + 1
                    creator.save()
            question.first().save()
            return HttpResponseRedirect(reverse('quiz:single_quiz', args=(quiz_id,)))
        else:
            form = CreateQuestionForm(instance=question.first())

        next_submit = "Далее"

        print(choices)

        context = {
            'form': form,
            'choices': choices,
            'timeout': question.first().timeout,
            'question_num': question_id,
            'next_submit': next_submit,

        }

        return render(request, 'quiz/edit_question.html', context=context)
    else:
        return HttpResponseRedirect(reverse('quiz:single_quiz', args=(quiz_id,)))

@login_required(login_url="users:login")
def delete_question(request, quiz_id, question_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    question = Question.objects.filter(quiz=quiz, id=question_id)
    if int(quiz.user_creator.get("id")) == int(request.user.id):
            question.first().delete()
    return HttpResponseRedirect(reverse('quiz:single_quiz', args=(quiz_id,)))