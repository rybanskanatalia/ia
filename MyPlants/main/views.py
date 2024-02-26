from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import logout, login
from .models import PlantList, Plants, Requests
from .forms import CreateNewList, AddPlantForm, ShareListForm, AddForm
from django.urls import reverse

def edit(request, id):
    plant = Plants.objects.get(pk=id)
    return render(request, 'main/edit.html', {'plant': plant})
    # plant = Plants.objects.get(id=id)

    # if request.method == "POST":
    #     print(request.POST)
    #     print(plant.id)
    # else:
    #     print("invalid")
    # return render(request, "main/edit.html", {"plant": plant})

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
            return redirect('home')  # Updated to 'home' without the slash
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

    try:
        # Try to get the default plant list for the user
        default_list = PlantList.objects.get(userID=request.user, location='Default Plant List')
        print('User has default plant list')
    except PlantList.DoesNotExist:
        # If the default list does not exist, create it
        default_list = PlantList.objects.create(userID=request.user, location='Default Plant List', plantAmount=0)
        print('Created default plant list')

    if request.method == 'POST':
        form = AddPlantForm(request.POST)
        if form.is_valid():
            plant = form.save(commit=False)
            
            plant.listID = default_list
            default_list.plantAmount += 1 # increase the plant amount of the list
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

        return redirect('home') 
    else:
        return render(request, 'error.html', {'message': 'Invalid request'})

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

# create new list
def create_new_list(request):
    if request.method == 'POST':
        form = CreateNewList(request.user, request.POST)
        if form.is_valid():
            new_list = form.save(request.user)
            return redirect('view')
    else:
        form = CreateNewList(user=request.user)
    
    return render(request, 'main/create.html', {'form': form})

# view the lists
def view(request):
    # fetch all the lists created by the current user and order them alphabetically by location
    user_lists = PlantList.objects.filter(userID=request.user).exclude(location='Default Plant List').order_by('location')
    return render(request, "main/view.html", {'user_lists': user_lists})

def list(request, id):
    pl = PlantList.objects.get(id=id)
    
    # Fetch plants that belong to the user
    user_plants = Plants.objects.filter(listID__userID=request.user)

    if pl in request.user.plantlist_set.all(): # check if the user owns the plant list
        if request.method == "POST":
            if 'addPlant' in request.POST:
                # Get the selected plant ID from the form
                new_plant_id = request.POST.get('new')
                if new_plant_id:
                    # Get the plant object
                    new_plant = Plants.objects.get(pk=new_plant_id)
                    # Add the plant to the list and increase plantAmount
                    pl.plants.add(new_plant)
                    pl.plantAmount += 1
                    pl.save()  # Save the changes to the PlantList

            elif 'deleteSelected' in request.POST:
                selected_plant_ids = request.POST.getlist('selected_plants')
                if selected_plant_ids:
                    # Remove selected plants from the list
                    pl.plants.filter(pk__in=selected_plant_ids).delete()
                    pl.plantAmount -= len(selected_plant_ids)
                    pl.save()  # Save the changes to the PlantList

            return redirect('list', id=id)  # Redirect back to the list page after adding/deleting plants

        return render(request, "main/list.html", {"pl": pl, "user_plants": user_plants})
    return render(request, "main/view.html", {})


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

def share(request):
    if request.method == 'POST':
        form = ShareListForm(request.POST, user=request.user)
        if form.is_valid():
            list_id = form.cleaned_data['list'].id
            email = form.cleaned_data['email']
            note = form.cleaned_data['note']

            # validate email
            try:
                user_to_share_with = User.objects.get(email=email)
            except User.DoesNotExist:
                return render(request, 'share.html', {'form': form, 'error': 'Invalid email address'})

            # retrieve the selected list
            try:
                selected_list = PlantList.objects.get(id=list_id, userID=request.user)
            except PlantList.DoesNotExist:
                return render(request, 'share.html', {'form': form, 'error': 'Invalid list'})

            # create a share request
            request_obj = Requests(senderID=request.user, listID=selected_list, receiverEmail=email, specialNote=note)
            request_obj.save()

            return redirect(reverse('share_success') + f'?receiver_email={email}')
    else:
        form = ShareListForm(user=request.user)

    return render(request, 'main/share.html', {'form': form})

def share_success(request):
    receiver_email = request.GET.get('receiver_email')
    return render(request, 'main/share_success.html', {'receiver_email': receiver_email})


def requests(request):
    if request.method == "POST":
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')

        if action == 'accept':
            # Handle the accept action if needed
            pass  # Placeholder, you can add your logic here for accepting the request

        elif action == 'reject':
            # Delete the request if reject is clicked
            Requests.objects.filter(id=request_id).delete()

            # Redirect back to the same page to refresh the requests
            return redirect('requests')

    # Get requests for the current user
    user_requests = Requests.objects.filter(receiverEmail=request.user.email)
    
    return render(request, "main/requests.html", {'user_requests': user_requests})

# load user's profile
def profile(response):
    return render(response, "main/profile.html", {})

# logout page
def out(response):
    return render(response, "main/out.html", {})

# functions that do exactly nothing
def notifications(response):
    return render(response, "main/notifications.html", {})

# use post when doing modifications to database, getting private info (encrypts the info and sends it to the server)
# use get when retrieving info (all the info goes into the url and pastes it further)