from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Profile
User = get_user_model()


class RegisterUserForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput({"placeholder": "Enter your email","class":"form-control mb-3"}))
    username = forms.CharField(widget=forms.TextInput({"placeholder": "Choose a username","class":"form-control mb-3"}))
    password1 = forms.CharField(label="Enter Password",widget=forms.PasswordInput({"placeholder": "Enter Password","class":"form-control mb-3"}))
    password2 = forms.CharField(label="Confirm Password",widget=forms.PasswordInput({"placeholder": "Confirm Password","class":"form-control mb-3"}))
    
    
    class Meta:
        model = User
        fields = ("email", "username") 
        
class ProfileForm(forms.ModelForm):
    bio = forms.CharField(widget=forms.Textarea(attrs={'rows':3}), required=True)
    class Meta:
        model = Profile
        fields = ( 'job_title', 'photo', 'phone', 'address', 'bio', 'location')     