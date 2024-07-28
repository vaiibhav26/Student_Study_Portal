from django.shortcuts import render,redirect, get_object_or_404
from django.contrib import messages
from .forms import *
from django.views import generic
from youtubesearchpython import VideosSearch  

import wikipedia
from .models import Todo
import requests
from django.contrib.auth.decorators import login_required



# Create your views here.

def home(request):
    return render(request, 'dashboard/home.html')

@login_required
def notes(request):
    if request.method =="POST":
        form = NotesForm(request.POST)
        if form.is_valid():
            notes = Notes(user = request.user, title = request.POST['title'], description = request.POST['description'])
            notes.save()
        messages.success(request, f"Notes Added Successfully")
    else:

        form = NotesForm()
    notes = Notes.objects.filter(user = request.user)  
    context = {'notes' : notes, 'form': form}
    return render(request, 'dashboard/notes.html', context)


@login_required
def delete_note(request, pk = None):
    Notes.objects.get(id = pk).delete()
    return redirect("notes")


class NotesDetailView(generic.DetailView) : 
    model = Notes 

@login_required
def homework(request):
    if request.method == "POST":
        form = HomeworkForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST['is_finished']
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False
            homeworks = Homework(
                user = request.user,
                subject = request.POST['subject'],
                title = request.POST['title'],
                description = request.POST['description'],
                due = request.POST['due'],
                is_finished = finished
            )
            homeworks.save()
            messages.success(request, "Homework Added SuccessFully!")
    else:
            
        form = HomeworkForm()

    homeworks = Homework.objects.filter(user = request.user)
    if len(homeworks) == 0:
        hw_done = True
    else:
        hw_done = False
    print(f"Fetched homeworks: {homeworks}")  # Add this line to print the fetched homeworks
    context = {'homeworks': homeworks, 'hw_done' : hw_done, 'form':form} 
    return render(request, 'dashboard/homework.html', context)   

    
@login_required
def update_homework(request ,pk = None):
    homework = Homework.objects.get(id = pk)
    if homework.is_finished :
        homework.is_finished = False
    else:
        homework.is_finished = True

    homework.save()
    return redirect('homework')


  
@login_required
def delete_homework(request, pk = None):
    Homework.objects.get(id = pk).delete()
    return redirect("homework")


def youtube(request):

    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']
        video = VideosSearch(text,limit = 20)
        result_list =[]
        for i in video.result()['result']:
            result_dict ={

                'input' : text,
                'title' : i['title'],
                'duration' : i['duration'],
                'thumbnail' :i['thumbnails'][0]['url'],
                'channel' :i['channel']['name'],
                'link' :i['link'],
                'views' :i['viewCount']['short'],
                'published' :i['publishedTime'],
            }
            desc =" "
            if i['descriptionSnippet']:
                for j in i['descriptionSnippet']:
                    desc += j['text']
            result_dict['description'] = desc
            result_list.append(result_dict)
            context = {
                'form':form,
                'results': result_list
            }
        return render(request,'dashboard/youtube.html', context)
            
    else:
        form = DashboardForm()
    context = { 'form': form }
    return render(request, 'dashboard/youtube.html', context)



@login_required
def todo(request):
    if request.method == 'POST':
        form = TodoForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST["is_finished"]
                if finished == "on":
                    finished = True
                else:
                    finished = False
            except:
                finished = False
            
            todos = Todo(
                user = request.user,
                title = request.POST['title'],
                is_finished = finished
            )
            todos.save()
            messages.success(request, "The 'to-do' has been created successfully!")
    else:

        form = TodoForm()
    todo = Todo.objects.filter(user = request.user)
    if len(todo) == 0:
        todos_done = True
    else:
        todos_done = False

    
    return render(request, "dashboard/todo.html",context = { 'todos':todo, 'form': form, 'todos_done':todos_done})


@login_required
def update_todo(request,  pk=None): 
    todo = Todo.objects.get(id=pk)
    if todo.is_finished == True:
        todo.is_finished = False
    else:
        todo.is_finished = True
    todo.save()
    return redirect('todo')



@login_required
def delete_todo(request, pk = None):
    todo = Todo.objects.get(id = pk)
    todo.delete()
    return redirect("todo")


@login_required

def books(request):

    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = "https://www.googleapis.com/books/v1/volumes?q="+text
        r = requests.get(url) 
        answer = r.json()
        result_list =[]
        for i in range(10):
            result_dict ={
                'title':answer['items'][i]['volumeInfo']['title'],
                'subtitle':answer['items'][i]['volumeInfo'].get('subtitle'),
                'description':answer['items'][i]['volumeInfo'].get('description'),
                'count':answer['items'][i]['volumeInfo'].get('pageCount'),
                'categories':answer['items'][i]['volumeInfo'].get('categories'),
                'rating':answer['items'][i]['volumeInfo'].get('pageRating'),
                'thumbnail':answer['items'][i]['volumeInfo'].get('imageLinks').get('thumbnail'),
                'preview':answer['items'][i]['volumeInfo'].get('previewLink')
            }
            
            result_list.append(result_dict)
            context = {
                'form':form,
                'results': result_list
            }
        return render(request,'dashboard/books.html', context)
            
    else:
        form = DashboardForm()
    context = { 'form': form }
    return render(request, 'dashboard/books.html', context)







def dictionary(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en_US/{text}"
        r = requests.get(url)
        answer = r.json()
        try:
            phonetics = answer[0].get('phonetics', [{}])[0].get('text', 'N/A')
            audio = answer[0].get('phonetics', [{}])[0].get('audio', '')
            definition = answer[0].get('meanings', [{}])[0].get('definitions', [{}])[0].get('definition', 'N/A')
            example = answer[0].get('meanings', [{}])[0].get('definitions', [{}])[0].get('example', 'N/A')
            synonyms = answer[0].get('meanings', [{}])[0].get('definitions', [{}])[0].get('synonyms', [])

            context = {
                'form': form,
                'input': text,
                'phonetics': phonetics,
                'audio': audio,
                'definition': definition,
                'example': example,
                'synonyms': synonyms
            }
        except (IndexError, KeyError):
            context = {
                'form': form,
                'input': text
            }
    else:
        form = DashboardForm()
        context = {'form': form}

    return render(request, "dashboard/dictionary.html", context)






def wiki(request):
    if request.method == 'POST':
        text = request.POST['text']
        form = DashboardForm(request.POST)
        search = wikipedia.page(text)
        context = {
            'form': form,
            'title': search.title,
            'link':search.url, 
            'details': search.summary,
        } 
        return render(request, "dashboard/wiki.html",context)
    else:
        
        form = DashboardForm()
        context = {'form':form}

    return render(request, "dashboard/wiki.html", context )



def conversion(request):
    if request.method == "POST":
        form =ConversionForm(request.POST)
        if request.POST['measurement'] == 'length':
            measurement_form = ConversionLengthForm()
            context = {
                'form':form,
                'm_form': measurement_form,
                'input':True
            }
            if 'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                input = request.POST['input']
                answer = ' '
                if input and int(input) >= 0:
                    if first == 'yard' and second == 'foot':
                        answer = f'{input} yard = {int(input)*3} foot'
                    if first == 'foot' and second == 'yard':
                        answer = f'{input} foot = {int(input)/3} yard'
                context = {
                    'form':form,
                    'm_form': measurement_form,
                    'input':True,
                    'answer':answer
                }
        
        if request.POST['measurement'] == 'mass':
            measurement_form = ConversionMassForm()
            context = {
                'form':form,
                'm_form': measurement_form,
                'input':True
            }
            if 'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                input = request.POST['input']
                answer = ' '
                if input and int(input) >= 0:
                    if first == 'pound' and second == 'kilogram':
                        answer = f'{input} pound = {int(input)*0.453592} kilogram'
                    if first == 'kilogram' and second == 'pound':
                        answer = f'{input} kilogram = {int(input)* 2.20462} pound'
                context = {
                    'form':form,
                    'm_form': measurement_form,
                    'input':True,
                    'answer':answer
                }

    else:
        form = ConversionForm()
        context = {
            'form':form,
            'input': False
        }

    return render(request, "dashboard/conversion.html",context)



def register(request):

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request,f"Welcome {username}! Your Account Has Been Created Successfully! ")
            return redirect('login')
    else:

        form = UserRegistrationForm()
    context = {
        'form': form
    }
    return render(request, "dashboard/register.html",context)



@login_required
def profile(request):
    homeworks = Homework.objects.filter(is_finished = False, user = request.user)
    todos = Todo.objects.filter(is_finished = False, user = request.user)
    if len(homeworks) == 0:
        homework_done = True
    else:
        homework_done = False
    if len(todos) == 0:
        todos_done = True
    else:
        todos_done = False

    context = {
        'homeworks': homeworks,
        'todos': todos,
        'homework_done': homework_done,
        'todos_done': todos_done,
    }
    return render(request, "dashboard/profile.html",context)