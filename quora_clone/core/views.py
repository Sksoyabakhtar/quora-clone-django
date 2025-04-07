from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Question, Answer
from django.contrib import messages

def home(request):
    questions = Question.objects.all().order_by('-created_at')
    return render(request, 'core/home.html', {'questions': questions})


def signup_view(request):
    if request.method == 'POST':
        full_name = request.POST['full_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('signup')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = full_name
        user.save()

        messages.success(request, 'Account created successfully. Please login.')
        return redirect('login')

    return render(request, 'core/signup.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('login')
    return render(request, 'core/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')



@login_required
def ask_question(request):
    if request.method == 'POST':
        title = request.POST['title']
        body = request.POST['body']
        Question.objects.create(title=title, body=body, author=request.user)
        messages.success(request, "Your question has been posted successfully!")
        return redirect('home')
    return render(request, 'core/ask_question.html')



def question_detail(request, pk):
    question = get_object_or_404(Question, pk=pk)
    answers = question.answers.all()
    if request.method == 'POST':
        body = request.POST['body']
        if request.user.is_authenticated:
            Answer.objects.create(body=body, author=request.user, question=question)
            messages.success(request, "Your answer has been submitted!")
            return redirect('question_detail', pk=pk)
        else:
            messages.error(request, "Please login to post an answer.")
            return redirect('login')
    return render(request, 'core/question_detail.html', {'question': question, 'answers': answers})



@login_required
def like_answer(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id)
    if request.user in answer.likes.all():
        answer.likes.remove(request.user)
        messages.success(request, "You unliked the answer.")
    else:
        answer.likes.add(request.user)
        messages.success(request, "You liked the answer.")
    return redirect('question_detail', pk=answer.question.id)



@login_required
def delete_question(request, pk):
    question = get_object_or_404(Question, pk=pk)
    if question.author == request.user:
        question.delete()
        messages.success(request, "Question deleted successfully.")
        return redirect('home')
    else:
        messages.error(request, "You are not allowed to delete this question.")
        return redirect('question_detail', pk=pk)
