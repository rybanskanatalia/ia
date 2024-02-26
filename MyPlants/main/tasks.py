from celery import shared_task
from django.core.mail import send_mail


@shared_task
def update_water_attribute(plant_id):
    # Retrieve the plant instance
    from .models import Plants
    plant = Plants.objects.get(id=plant_id)
    
    # update the water attribute 
    plant.water -= 1

    if plant.water == 0:
        # send an email notification if the plant needs watering
        send_mail(
            'Watering Reminder',
            f'Don\'t forget to water your {plant.name}!',
            'user@gmail.com', 
            [plant.user.email],  # recipient's email address
            fail_silently=False,
        )
    
    elif plant.water == -1:
        # Reset water attribute to period value
        plant.water = plant.period

    plant.save()