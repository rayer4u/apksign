from django import forms
from models import UpFile
    
class UploadModelFileForm(forms.ModelForm):
    certification = forms.CharField()
    
    class Meta:
        model = UpFile
        exclude = ('signed', 'status', 'up_date', 'from_ip')
        
