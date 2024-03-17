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

# check if a user is authenticated
def index(request):
    if request.user.is_authenticated:
        # redirect to home page if the user is already logged in
        return redirect('home') 
    else:
        if request.method == "POST":
            form = AuthenticationForm(request, request.POST)
            if form.is_valid():
                login(request, form.get_user())
                return redirect('home') 
        else:
            form = AuthenticationForm()
        return render(request, 'main/login.html', {'form': form})

# after registration redirect to home page 
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
    # fetch plants specific to the authenticated user
    plants = Plants.objects.filter(listID__userID=request.user)
    return render(request, 'main/home.html', {'plants': plants})

# add function for the plants
def add_plant(request):

    try:
        # check if the user already has a default plant list 
        default_list = PlantList.objects.get(userID=request.user, location='Default Plant List')
        print('User has default plant list')

    except PlantList.DoesNotExist:
        # if the default list does not exist, create it
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
    
    user_plants = Plants.objects.filter(listID__userID=request.user)

    if pl in request.user.plantlist_set.all(): # check if the user owns the plant list
        if request.method == "POST":
            if 'addPlant' in request.POST:
                # get the selected plant ID from the form
                new_plant_id = request.POST.get('new')
                if new_plant_id:
                    new_plant = Plants.objects.get(pk=new_plant_id)
                    # add the plant to the list 
                    pl.plants.add(new_plant)
                    pl.plantAmount += 1
                    pl.save() 

            elif 'deleteSelected' in request.POST:
                selected_plant_ids = request.POST.getlist('selected_plants')
                if selected_plant_ids:
                    # remove selected plants from the list
                    pl.plants.filter(pk__in=selected_plant_ids).delete()
                    pl.plantAmount -= len(selected_plant_ids)
                    pl.save()  

            return redirect('list', id=id)  # redirect back to the list page after adding/deleting plants

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

# share the list
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

# share requests
def requests(request):
    if request.method == "POST":
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')

        if action == 'accept':
            # get the request object
            request_obj = Requests.objects.get(id=request_id)

            # get the shared list
            shared_list = PlantList.objects.get(location=request_obj.listID)

            # check if the user already has this list
            user_list_exists = PlantList.objects.filter(userID=request.user, location=shared_list.location).exists()

            if not user_list_exists:
                # create a new PlantList for the user based on the shared list
                new_list = PlantList.objects.create(
                    userID=request.user,
                    location=shared_list.location,
                    plantAmount=shared_list.plantAmount
                )

                new_list.plants.set(shared_list.plants.all())
                new_list.save()

            # delete the request after processing
            request_obj.delete()

            return redirect('requests')

        elif action == 'reject':
            # delete the request if reject is clicked
            Requests.objects.filter(id=request_id).delete()

            return redirect('requests')

    # get requests for the current user
    user_requests = Requests.objects.filter(receiverEmail=request.user.email)
    
    return render(request, "main/requests.html", {'user_requests': user_requests})

# load user's profile
def profile(response):
    return render(response, "main/profile.html", {})

# logout page
def out(response):
    return render(response, "main/out.html", {})

# functions for further development
def notifications(response):
    return render(response, "main/notifications.html", {})

# create new list
def create(request):
    if request.method == "POST":
        form = CreateNewList(request.POST)

        if form.is_valid():
            location = form.cleaned_data["location"]
            plant_list = PlantList(location=location, userID=request.user)
            plant_list.save()
            return redirect('view')  
    else:
        form = CreateNewList()  

    return render(request, 'main/create.html', {'form': form})