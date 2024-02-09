from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_migrate
from django.dispatch import receiver

# Create your models here.


# class ToDoList(models.Model): 
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     name = models.CharField(max_length=200)
    
#     def __str__(self): 
#         return self.name
    
# class Item(models.Model):
#     todolist = models.ForeignKey(ToDoList, on_delete=models.CASCADE)
#     text = models.CharField(max_length=300)
#     cocmplete = models.BooleanField()

#     def __str__(self):
#         return self.text

####
@receiver(post_migrate)
def create_default_list(sender, **kwargs):
    if sender.name == 'main':
        if not PlantList.objects.exists():
            PlantList.objects.create(location='default location', plantAmount=0)
    
class PlantList(models.Model):
    userID = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=200)
    plantAmount = models.IntegerField()
    
    def __str__(self):
        return self.location
    
class Plants(models.Model):
    listID = models.ForeignKey(PlantList, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=200)
    water = models.IntegerField()
    period = models.IntegerField()

    def __str__(self):
        return self.name

class Location(models.Model):
    plantID = models.ForeignKey(Plants, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    
    def __str__(self):
        return self.text

class Requests(models.Model):
    senderID = models.ForeignKey(User, on_delete=models.CASCADE)
    listID = models.ForeignKey(PlantList, on_delete=models.CASCADE)
    receiverEmail = models.CharField(max_length=200)
    specialNote = models.CharField(max_length=200)

    def __str__(self):
        return self.text
    

    

