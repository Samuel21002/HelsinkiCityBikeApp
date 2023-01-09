from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as user_login, logout
from django.contrib.auth.forms import AuthenticationForm

def load_index_page(request):
    return render(request, 'core/index.html')

def login(request):
    
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
            if user is not None:
                valuenext= str(request.POST['next'])
                user_login(request, user)
                return redirect(valuenext)
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form':form})

def logout(request):
    logout(request)
    return redirect('core:login')