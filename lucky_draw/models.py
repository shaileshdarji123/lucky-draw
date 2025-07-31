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
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.department} (Day {self.day_1})"
    
    def generate_qr_code(self):
        """Generate QR code for the staff member"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        # QR code data: staff_id:day
        qr_data = f"{self.id}:{self.day_1}"
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to BytesIO
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        # Use name_dep_day.png as filename
        name_slug = slugify(self.name)
        dep_slug = slugify(self.department)
        filename = f'{name_slug}_{dep_slug}_{self.day_1}.png'
        
        # Save to model
        self.qr_code.save(filename, ContentFile(buffer.getvalue()), save=False)
        return self.qr_code
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        # Only generate QR code if it's a new object and QR code is not set
        if is_new and not self.qr_code:
            self.generate_qr_code()
            super().save(update_fields=['qr_code'])

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
