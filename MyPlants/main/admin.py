from django.contrib import admin
# give the database access to the tables
from .models import ToDoList, Item, PlantList, Plants, Location, Requests
# Register your models here.
admin.site.register(ToDoList)
admin.site.register(Item)
admin.site.register(PlantList)
admin.site.register(Plants)
admin.site.register(Location)
admin.site.register(Requests)