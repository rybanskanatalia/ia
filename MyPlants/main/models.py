from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime, timedelta
from celery import shared_task
from .tasks import update_water_attribute

@receiver(post_migrate)
def create_default_list(sender, **kwargs):
    if sender.name == 'main':
        if not PlantList.objects.exists():
            PlantList.objects.create(location='default location', plantAmount=0) 

class PlantList(models.Model):
    userID = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=200)
    plantAmount = models.IntegerField(default=0)

    def __str__(self):
        return self.location

class Plants(models.Model):
    listID = models.ForeignKey(PlantList, on_delete=models.CASCADE, related_name='plants')  
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
        return str(self.listID)
    

receiver(post_save, sender=Plants)
def schedule_water_update(sender, instance, created, **kwargs):
    if created:
        # Schedule the task to update water attribute at midnight
        midnight = datetime.combine(datetime.today(), datetime.min.time()) + timedelta(days=1)
        update_water_attribute.apply_async(args=[instance.id], eta=midnight)
