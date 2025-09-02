from django import forms
from .models import Staff
from .models import EventSettings

class StaffUploadForm(forms.Form):
    file = forms.FileField(
        label='Upload Staff List (Excel/CSV)',
        help_text='Upload an Excel or CSV file with columns: Staff Name, Department, Day 1',
        widget=forms.FileInput(attrs={'accept': '.xlsx,.xls,.csv'})
    )

class QRCodeScanForm(forms.Form):
    qr_data = forms.CharField(
        max_length=50,
        widget=forms.HiddenInput(),
        required=False
    )
    
    def clean_qr_data(self):
        qr_data = self.cleaned_data.get('qr_data')
        if not qr_data:
            raise forms.ValidationError("QR code data is required")
        
        try:
            staff_id, day = qr_data.split(':')
            staff_id = int(staff_id)
            day = int(day)
            
            if day not in [1, 2]:
                raise forms.ValidationError("Invalid day value")
                
            return qr_data
        except (ValueError, AttributeError):
            raise forms.ValidationError("Invalid QR code format") 

class EventSettingsForm(forms.ModelForm):
    class Meta:
        model = EventSettings
        fields = ['day1_date', 'day2_date']
        widgets = {
            'day1_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'day2_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

# Manual staff entry form
class StaffManualForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['name', 'department', 'day_1']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Staff Name'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Department'}),
            'day_1': forms.Select(attrs={'class': 'form-select'}, choices=[(1, 'Day 1'), (2, 'Day 2')]),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '')
        if name is None:
            return name
        name = name.strip()
        if len(name) > 35:
            raise forms.ValidationError('Name must be 35 characters or less.')
        return name