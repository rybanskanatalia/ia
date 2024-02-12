from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import logout, login
from .models import PlantList, Plants
from .forms import CreateNewList, AddPlantForm

# home view with all plants
@login_required
def home(request):
    # Fetch plants specific to the current user
    plants = Plants.objects.filter(listID__userID=request.user)
    return render(request, 'main/home.html', {'plants': plants})

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
    
# delete a plant
def delete_plants(request):
    if request.method == 'POST':
        plant_ids = request.POST.getlist('plant_id')
        Plants.objects.filter(id__in=plant_ids).delete()
        return redirect('home')  # Redirect to the home page after deletion
    else:
        # Handle GET requests or other cases
        return render(request, 'error.html', {'message': 'Invalid request'})
    
# this function has to be redone, it is from the tutorial
# def index1(response, id):
#     ls = ToDoList.objects.get(id=id)

#     if ls in response.user.todolist.all():
#         if response.method == "POST":
#             print(response.POST)
#             if response.POST.get("save"):
#                 for item in ls.item_set.all():
#                     # if response.POST.get("c" + str(item.id)) == "clicked":
#                     if f"c{item.id}" in response.POST:
#                         item.cocmplete = True
#                     else:
#                         item.cocmplete = False
#                     item.save()

#             elif response.POST.get("newItem"):
#                 txt = response.POST.get("new")

#                 if len(txt) > 0:
#                     ls.item_set.create(text=txt, cocmplete = False)
#                 else:
#                     print("invalid")

#         return render(response, "main/list.html", {"ls": ls})
#     return render(response, "main.view.html", {})

# create new list
def create(request):
    if request.method == "POST":
        form = CreateNewList(request.POST)

        if form.is_valid():
            location = form.cleaned_data["location"]
            # Assuming you have user information available in the request
            plant_list = PlantList(location=location, userID=request.user)
            plant_list.save()
            return redirect('view')  
    else:
        form = CreateNewList()  # Create an empty form to render in the template

    return render(request, 'main/create.html', {'form': form})

# view the lists
def view(request):
    # fetch all the lists created by the current user and order them alphabetically by location
    user_lists = PlantList.objects.filter(userID=request.user).exclude(location='Default Plant List').order_by('location')
    return render(request, "main/view.html", {'user_lists': user_lists})

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