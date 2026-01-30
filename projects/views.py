from django.shortcuts import render
from django.views.generic import View


class ProjectIndex(View):
    def get(self,request):
        return render(request,'projects/index.html')
    
