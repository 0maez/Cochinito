from django.shortcuts import render, redirect
from .forms import RegisterForm

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")  # Redirige al login después del registro
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})
