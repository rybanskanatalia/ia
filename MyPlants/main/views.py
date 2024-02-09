from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import logout, login
from .models import ToDoList, Item, PlantList, Plants
from .forms import CreateNewList, AddPlantForm

# home view with all plants

@login_required
def home(request):
    # Fetch plants specific to the current user
    plants = Plants.objects.filter(listID__userID=request.user)
    return render(request, 'main/home.html', {'plants': plants})

# def home(request):
#     # Fetch all plants from the database
#     plants = Plants.objects.all()
#     return render(request, 'main/home.html', {'plants': plants})

# add function for the plants
def add_plant(request):
    # retrieve the default plant list where all plants are stored
    default_list, created = PlantList.objects.get_or_create(userID=request.user, location='Default Plant List', plantAmount=0)

    if request.method == 'POST':
        form = AddPlantForm(request.POST)
        if form.is_valid():
            plant = form.save(commit=False)
            # Assign the default plant list object to the listID field
            plant.listID = default_list
            form.save()
            return redirect('home')
    else:
        form = AddPlantForm()
    return render(request, 'main/add.html', {'form': form})

# after registration the user is redirected to home page of their profile
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
        else:
            form = UserCreationForm()
        return render(request, 'main/registration_form.html', {'form': form})

# check if a user is authenticated
def index(request):
    if request.user.is_authenticated:
        # Redirect to the desired page if the user is already logged in
        return redirect('home') 
    else:
        if request.method == "POST":
            form = AuthenticationForm(request, request.POST)
            if form.is_valid():
                login(request, form.get_user())
                # If login is successful, redirect to the desired page
                return redirect('home') 
        else:
            form = AuthenticationForm()
        return render(request, 'main/login.html', {'form': form})
    
# this function will have to be redone, it is from the tutorial
def index1(response, id):
    ls = ToDoList.objects.get(id=id)

    if ls in response.user.todolist.all():
        if response.method == "POST":
            print(response.POST)
            if response.POST.get("save"):
                for item in ls.item_set.all():
                    # if response.POST.get("c" + str(item.id)) == "clicked":
                    if f"c{item.id}" in response.POST:
                        item.cocmplete = True
                    else:
                        item.cocmplete = False
                    item.save()

            elif response.POST.get("newItem"):
                txt = response.POST.get("new")

                if len(txt) > 0:
                    ls.item_set.create(text=txt, cocmplete = False)
                else:
                    print("invalid")

        return render(response, "main/list.html", {"ls": ls})
    return render(response, "main.view.html", {})

def create(response):
    # default is always get
    if response.method == "POST":
        form = CreateNewList(response.POST)

        if form.is_valid():
            n = form.cleaned_data["name"]
            t = ToDoList(name=n)
            t.save()
            response.user.todolist.add(t)

        return HttpResponseRedirect("/%i" %t.id)

    else:
        form = CreateNewList()
    return render(response, "main/create.html", {"form":form})

# logout
def logout_view(request):
    logout(request)
    return redirect('out')

# functions that delete the user account
def delete(request):
    return render(request, 'main/delete.html')

def delete_account(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            request.user.delete()
            logout(request)
            return redirect('login')
    return HttpResponseBadRequest("invalid request")

# other views that do exactly nothing
def view(response):
    return render(response, "main/view.html", {})

def share(response):
    return render(response, "main/share.html", {})

def requests(response):
    return render(response, "main/requests.html", {})

def notifications(response):
    return render(response, "main/notifications.html", {})

def out(response):
    return render(response, "main/out.html", {})

def profile(response):
    return render(response, "main/profile.html", {})




# use post when doing modifications to database, getting private info (encrypts the info and sends it to the server)
# use get when retrieving info (all the info goes into the url and pastes it further)