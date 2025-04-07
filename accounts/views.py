from django.shortcuts import render,HttpResponse,redirect
from .forms import LoginForm
from django.contrib.auth import login,logout,authenticate
# Create your views here.


def login_view(request):
    if request.method == "POST":
        form_data = LoginForm(request.POST)
        #print(form_data)
        if form_data.is_valid():
            #print(form_data.cleaned_data)
            username = form_data.cleaned_data["username"]
            password = form_data.cleaned_data["password"]
            check_user = authenticate(request,username=username,password=password)
            
            if check_user is not None:
                login(request,check_user)
                return redirect("home:index")
            else:
                
                return redirect("accounts:login")
        else:
            return HttpResponse("Form filling error")
    else:
        form_data = LoginForm()
        
    
    
    return render(request,'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect("home:index")