from django.contrib import messages
from django.shortcuts import redirect, render
from matplotlib.pyplot import title
from regex import F
from yaml import serialize
from .models import *
from .forms import *
from django.views import generic
from .serializer import *
from youtubesearchpython import VideosSearch
import requests
import wikipedia
from django.contrib.auth.decorators import login_required
# Create your views here.
def home(request):
    return render(request,'dashboard/home.html')

@login_required
def notes(request):
    if request.method == 'POST':

        form = NotesForm(request.POST)
        if form.is_valid():
            notes = Notes(user = request.user,title = request.POST['title'], description = request.POST['description'])
            notes.save()
        messages.success(request,f"notes added from { request.user.username } successfully")
    else:
        form = NotesForm()
    notes = Notes.objects.filter(user = request.user)
    context = {'notes':notes,'form':form}
    print(notes)
    return render(request,'dashboard/notes.html',context)

@login_required
def delete_note(request,pk=None):
    Notes.objects.get(id=pk).delete()
    return redirect("notes")


class NotesDetailView(generic.DetailView):
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
            
            homeworks =  Homework(
                user = request.user,
                title = request.POST['title'],
                subject = request.POST['subject'],
                description = request.POST['description'],
                due = request.POST['due'],
                is_finished = finished
            ) 
            homeworks.save()
            messages.success(request,f'homework added from {{request.user.username}}')


    else:
        form = HomeworkForm()
    homework = Homework.objects.filter(user = request.user)
    if len(homework)==0:
        homework_done = True
    else:
        homework_done = False
    serializer = Homework_masterSerializer(homework,many=True)
    # for i in serializer.data:
    #     print(i)
    
    context = {'homeworks':homework,
                'homework_done': homework_done,
                'form':form}
   
    return render(request,'dashboard/homework.html',context)


@login_required
def update_homework(request,pk=None):
    homework = Homework.objects.get(id = pk)
    #print(homework)
    if homework.is_finished == True:
        homework.is_finished = False
    else: 
        homework.is_finished = True
    homework.save()
    return redirect('homework')

def delete_homework(request,pk=None):
    Homework.objects.get(id=pk).delete()
    
    return redirect("homework")


def youtube(request):
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        text = request.POST['text']
        video = VideosSearch(text, limit=10)
        result_list = []
        for i in video.result()['result']:
            result_dict = {
                'input':text,
                'title':i['title'],
                'duration':i['duration'],
                'thumbnail':i['thumbnails'][0]['url'],
                'channel':i['channel']['name'],
                'link':i['link'],
                'views':i['viewCount']['short'],
                'published':i['publishedTime'],
            }
            desc = ''
            if i['descriptionSnippet']:
                for j in i['descriptionSnippet']:
                    desc += j['text']
            result_dict['description']=desc
            result_list.append(result_dict)
            context = {
                'form':form,
                'results': result_list
            }
        #print(result_list)
        return  render(request, 'dashboard/youtube.html',context)
            
    else:
        form = DashboardForm()
    context = {'form':form}
    return render(request,'dashboard/youtube.html',context)

@login_required
def todo(request):
    if request.method == 'POST':
        form = TodoForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST['is_finished']
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False
            todo = Todo(
                user = request.user,
                title = request.POST['title'],
                is_finished = finished
            )
            todo.save()
        messages.success(request,f'homework added from {{request.user.username}}')
    else:
        form = TodoForm()
    todos = Todo.objects.filter(user = request.user)
    if len(todos)==0:
        todos_completed = True
    else:
        todos_completed = False
    context = {'todos':todos,
                'form':form,
                'todos_completed':todos_completed}
    return render(request,'dashboard/todo.html',context)

@login_required
def update_todo(requests,pk = None):
    todo = Todo.objects.get(id = pk)
    if todo.is_finished == True:
        todo.is_finished = False
    else :
        todo.is_finished =True
    todo.save()
    return redirect('todo')

def delete_todo(request, pk = None):
    Todo.objects.get(id=pk).delete()
    return redirect("todo")


def books(request):
    if request.method == 'POST': 
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = 'https://www.googleapis.com/books/v1/volumes?q='+text
        r = requests.get(url)
        answer = r.json()
        result_list = []
        for i in range(10):
            result_dict = {
                
                'title':answer['items'][i]['volumeInfo']['title'],
                'subtitle':answer['items'][i]['volumeInfo'].get('subtitle'),
                'description':answer['items'][i]['volumeInfo'].get('description'),
                'rating':answer['items'][i]['volumeInfo'].get('pageRating'),
                'count':answer['items'][i]['volumeInfo'].get('pageCount'),
                'categories':answer['items'][i]['volumeInfo'].get('categories'),
                'thumbnail':answer['items'][i]['volumeInfo'].get('imageLinks').get('thumbnail'),
                'preview':answer['items'][i]['volumeInfo'].get('previewLink'),
            }
           
           
            result_list.append(result_dict)
            context = {
                'form':form,
                'results': result_list
            }
        #print(result_list)
        return  render(request, 'dashboard/books.html',context)
    else:

        form = DashboardForm()
    
    context = {
        'form':form
    }
    return render(request,'dashboard/books.html',context)


def dictionary(request):
    if request.method == 'POST': 
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = 'https://api.dictionaryapi.dev/api/v2/entries/en_US/'+text
        r = requests.get(url)
        answer = r.json()
        try:
            phonetics = answer[0]['phonetics'][0]['text']
            audio = answer[0]['phonetics'][0]['audio']
            synonyms = answer[0]['meanings'][0]['definitions'][0]['synonyms']
            definition = answer[0]['meanings'][0]['definitions'][0]['definition']
            example = answer[0]['meanings'][0]['definitions'][0]['example']
            
            context = {
                'form':form,
                'input':text,
                'phonetics': phonetics,
                'audio':audio,
                'definitions':definition,
                'example':example,
                'synonyms':synonyms
            }
        except:
            context = {
                'form':form,
                'input':''
            }

        #print(result_list)
        #print(answer)
        return render(request, 'dashboard/dictionary.html',context)
    else: 
        form = DashboardForm()
        context = {
        'form':form
        }
    return render(request,'dashboard/dictionary.html',context)


def wiki(request):
    if request.method == 'POST':
        text = request.POST['text']
        form = DashboardForm(request.POST)
        search = wikipedia.page(text)
        context = {
            'form':form,
            'title':search.title,
            'link':search.url,
            'details':search.summary
        }
        return render(request,'dashboard/wiki.html',context)

    else:
        form = DashboardForm()
        context = {
            'form':form
        }
    return render(request,'dashboard/wiki.html',context)


def conversion(request):
    if request.method == 'POST':
        form = ConversionForm(request.POST)
        if request.POST['measurement'] == "length":
            measurement_form = ConversionLengthForm()
            context = {
                'form':form,
                'm_form':measurement_form,
                'input':True
            }
            if 'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                input = request.POST['input']
                answer = ''
                if input and int(input) >=0:
                    if first == 'yard' and second == 'foot':
                        answer = f'{input} yard = {int(input)*3} foot'
                    if first == 'foot' and second == 'yard':
                        answer = f'{input} yard = {int(input)/3} foot'
                context={
                    'form':form,
                    'm_form':measurement_form,
                    'input':True,
                    'answer':answer
                }
        if request.POST['measurement'] == 'mass':
            measurement_form = ConversionMassForm()
            context = {
                'form':form,
                'm_form':measurement_form,
                'input':True  
                
            }
            if 'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                input = request.POST['input']
                answer = ''
                if input and int(input) >=0:
                    if first == 'pound' and second == 'kilogram':
                        answer = f'{input} pound = {int(input)*0.453592} kilogram'
                    if first == 'kilogram' and second == 'pound':
                        answer = f'{input} kilogram = {int(input)*2.20462} pound'
                context={
                    'form':form,
                    'm_form':measurement_form,
                    'input':True,
                    'answer':answer
                }
        

    else:
        form = ConversionForm()
        context = {
            'form':form,
            'input':False
        }
    return render(request,'dashboard/conversion.html',context)


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request,f'account created for {username}')
            return redirect ('login')
    else:
        form = UserRegistrationForm()
    context = {
            'form':form
    }
    return render(request,'dashboard/register.html',context)

@login_required
def profile(request):
    todos = Todo.objects.filter(is_finished=False, user = request.user)
    homework = Homework.objects.filter(is_finished=False, user = request.user)
    if len(homework)==0:
        homework_done = True
    else:
        homework_done = False

    if len(todos)==0:
            todos_done = True
    else:
        todos_done = False
    context = {
        'todos':todos,
        'homeworks':homework,
        'homework_done':homework_done,
        'todos_done':todos_done 
    }
    return render(request,'dashboard/profile.html',context)