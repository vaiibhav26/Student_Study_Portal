from django.shortcuts import render,redirect, get_object_or_404
from django.contrib import messages
from .forms import *
from django.views import generic
from youtubesearchpython import VideosSearch  

from .models import Todo
import requests


# Create your views here.

def home(request):
    return render(request, 'dashboard/home.html')

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



def delete_note(request, pk = None):
    Notes.objects.get(id = pk).delete()
    return redirect("notes")

class NotesDetailView(generic.DetailView) : 
    model = Notes 


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

    

def update_homework(request ,pk = None):
    homework = Homework.objects.get(id = pk)
    if homework.is_finished :
        homework.is_finished = False
    else:
        homework.is_finished = True

    homework.save()
    return redirect('homework')


  

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


# @login_required
# def todo(request):
#     if request.method == 'POST':
#         form = TodoForm(request.POST)
#         if form.is_valid():
#             todo = form.save(commit=False)
#             todo.user = request.user
#             todo.save()
#             messages.success(request, "The 'to-do' has been created successfully!")
#             return redirect('todo')  # Redirect to avoid resubmission on refresh
#     else:
#         form = TodoForm()

#     todos = Todo.objects.filter(user=request.user)
#     todos_done = not todos.exists()

#     return render(request, "dashboard/todo.html", context={'todos': todos, 'form': form, 'todos_done': todos_done})

def update_todo(request,  pk=None): 
    todo = Todo.objects.get(id=pk)
    if todo.is_finished == True:
        todo.is_finished = False
    else:
        todo.is_finished = True
    todo.save()
    return redirect('todo')




def delete_todo(request, pk = None):
    todo = Todo.objects.get(id = pk)
    todo.delete()
    return redirect("todo")



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





# def dictionary(request):
#     if request.method == "POST":
#         form = DashboardForm(request.POST)
#         text = request.POST['text']
#         url = "https://api.dictionaryapi.dev/api/v2/entries/en_US/"+text
#         r = requests.get(url) 
#         answer = r.json()
#         result_list =[]
#         try:
#             phonetics = answer[0]['phonetics'][0]['text']
#             audio = answer[0]['phonetics'][0]['audio']
#             definition = answer[0]['meanings'][0]['definitions'][0]['definition']
#             example = answer[0]['meanings'][0]['definitions'][0]['example']
#             synonyms = answer[0]['meanings'][0]['definitions'][0]['synonyms']

#             context = {
#                 'form':form,
#                 'input':text,
#                 'phonetics':phonetics,
#                 'audio':audio,
#                 'definitions':definition,
#                 'example':example,
#                 'synonyms':synonyms
#             }

#         except:
#             context = {
#                 'form':form,
#                 'input':text
#             }
#             return render(request, "dashboard/dictionary.html",context)

#     else:

#         form = DashboardForm()
#         context = {'form':form}
#     return render(request, "dashboard/dictionary.html",context)




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
