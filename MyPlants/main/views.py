from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import logout, login
from .models import PlantList, Plants, Requests
from .forms import CreateNewList, AddPlantForm, ShareListForm

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

# home view with all plants
@login_required
def home(request):
    # Fetch plants specific to the current user
    plants = Plants.objects.filter(listID__userID=request.user)
    return render(request, 'main/home.html', {'plants': plants})

# add function for the plants
def add_plant(request):

    has_plants = Plants.objects.filter(listID__userID=request.user).exists()

    if has_plants:
        default_list = PlantList.objects.get(userID=request.user, location='Default Plant List') # retrieve the default plant list
    else:
        default_list = PlantList.objects.create(userID=request.user, location='Default Plant List', plantAmount=0)
    
    if request.method == 'POST':
        form = AddPlantForm(request.POST)
        if form.is_valid():
            plant = form.save(commit=False)
            
            plant.listID = default_list
            default_list.plantAmount += 1 #increase the plant amount of the list
            default_list.save()

            form.save()
            return redirect('home')
    else:
        form = AddPlantForm()
    return render(request, 'main/add.html', {'form': form})

# delete a plant
def delete_plants(request):
    if request.method == 'POST':
        plant_ids = request.POST.getlist('plant_id')
        del_amount = len(plant_ids)

        Plants.objects.filter(id__in=plant_ids).delete()

        default_list = PlantList.objects.get(userID=request.user, location='Default Plant List')
        default_list.plantAmount -= del_amount
        default_list.save()

        return redirect('home')  # Redirect to the home page after deletion
    else:
        # Handle GET requests or other cases
        return render(request, 'error.html', {'message': 'Invalid request'})

def list(request, id):
    pl = PlantList.objects.get(id=id)

    if pl in request.user.plantlist_set.all(): # Assuming you want to check if the user owns the plant list
        if request.method == "POST":
            print(request.POST)
            if request.POST.get("save"):
                print(pl.location)
                for plant in pl.plant_set.all():
                   print(plant.id)
            else: 
                print("invalid")
        return render(request, "main/list.html", {"pl": pl})
    return render(request, "main/view.html", {}) 

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
# def share(request):
#     if request.method == 'POST':
#         list_id = request.POST.get('list')
#         email = request.POST.get('email')
        
#         # Validate email
#         try:
#             user_to_share_with = User.objects.get(email=email)
#         except User.DoesNotExist:
#             # Handle invalid email
#             return render(request, 'share.html', {'error': 'Invalid email address'})
        
#         # Retrieve the selected list
#         try:
#             selected_list = PlantList.objects.get(id=list_id, userID=request.user)
#         except PlantList.DoesNotExist:
#             # Handle invalid list
#             return render(request, 'share.html', {'error': 'Invalid list'})
        
#         # Share the list with the specified user
#         selected_list.shared_with.add(user_to_share_with)
#         selected_list.save()
        
#         # Redirect to a success page or display a success message
#         return redirect('share_success')

#     return render(request, 'share.html')

def share(request):
    if request.method == 'POST':
        form = ShareListForm(request.POST, user=request.user)
        if form.is_valid():
            list_id = form.cleaned_data['list'].id
            email = form.cleaned_data['email']

            # Validate email
            try:
                user_to_share_with = User.objects.get(email=email)
            except User.DoesNotExist:
                # Handle invalid email
                return render(request, 'share.html', {'form': form, 'error': 'Invalid email address'})

            # Retrieve the selected list
            try:
                selected_list = PlantList.objects.get(id=list_id, userID=request.user)
            except PlantList.DoesNotExist:
                # Handle invalid list
                return render(request, 'share.html', {'form': form, 'error': 'Invalid list'})

            # Create a share request
            request_obj = Requests(senderID=request.user, listID=selected_list, receiverEmail=email)
            request_obj.save()

            # Redirect to a success page or display a success message
            return redirect('share_success')
    else:
        form = ShareListForm(user=request.user)

    return render(request, 'main/share.html', {'form': form})

def share_success(request):
    # You can customize this view as needed, such as displaying a success message
    return render(request, 'main/share_success.html')

# load user's profile
def profile(response):
    return render(response, "main/profile.html", {})

# logout page
def out(response):
    return render(response, "main/out.html", {})

# functions that do exactly nothing
def requests(response):
    return render(response, "main/requests.html", {})

def notifications(response):
    return render(response, "main/notifications.html", {})

# use post when doing modifications to database, getting private info (encrypts the info and sends it to the server)
# use get when retrieving info (all the info goes into the url and pastes it further)

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
