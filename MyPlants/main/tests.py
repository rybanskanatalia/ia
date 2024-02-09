from django.test import TestCase

# Create your tests here.
from .tasks import update_water_attribute

# Call the task
plant_id = 1
update_water_attribute(plant_id)