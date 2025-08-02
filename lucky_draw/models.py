from django.db import models
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image
import os
from django.utils import timezone
from django.utils.text import slugify

class Staff(models.Model):
    name = models.CharField(max_length=200)
    department = models.CharField(max_length=100)
    day_1 = models.IntegerField(choices=[(1, 'Day 1'), (2, 'Day 2')], default=1)
    # qr_code field removed; QR codes are now generated on the fly
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.department} (Day {self.day_1})"
    
    # QR code generation and saving removed; use view logic to generate on the fly

class CheckIn(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    day = models.IntegerField(choices=[(1, 'Day 1'), (2, 'Day 2')])
    checked_in_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['staff', 'day']  # Prevent duplicate check-ins
    
    def __str__(self):
        return f"{self.staff.name} - Day {self.day} - {self.checked_in_at}"

class Winner(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    day = models.IntegerField(choices=[(1, 'Day 1'), (2, 'Day 2')])
    drawn_at = models.DateTimeField(auto_now_add=True)
    draw_order = models.IntegerField()  # Order in which they were drawn
    
    class Meta:
        unique_together = ['staff', 'day']  # Prevent duplicate winners
        ordering = ['day', 'draw_order']
    
    def __str__(self):
        return f"{self.staff.name} - Day {self.day} Winner #{self.draw_order}"

class EventSettings(models.Model):
    day1_date = models.DateField(null=True, blank=True)
    day2_date = models.DateField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Event Dates: Day 1 - {self.day1_date}, Day 2 - {self.day2_date}"

    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
