from django.shortcuts import render
from django.views.generic import View,ListView

from accounts.models import Profile

class RegisterAccount(View):
    def get(self,request):
        return render(request,'accounts/registrations/register.html')



class ProfileList(ListView):
    model = Profile
    template_name = 'accounts/profile/profile_list.html'
    context_object_name = 'profiles'
    paginate_by = 6