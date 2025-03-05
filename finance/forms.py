from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, IncomeSource, BasicExpense, WishExpense, SavingsInvestment

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    age = forms.IntegerField(required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "age", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            Profile.objects.create(user=user, age=self.cleaned_data["age"])
        return user


class IncomeForm(forms.Form):
    income_sources = forms.ModelMultipleChoiceField(
        queryset=IncomeSource.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    
class BasicExpenseForm(forms.Form):
    basic_expenses = forms.ModelMultipleChoiceField(
        queryset=BasicExpense.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

class WishExpenseForm(forms.Form):
    wish_expenses = forms.ModelMultipleChoiceField(
        queryset=WishExpense.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    

class SavingsInvestmentForm(forms.Form):
    savings_investments = forms.ModelMultipleChoiceField(
        queryset=SavingsInvestment.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

class ProfileForm(forms.ModelForm):
    class Meta: 
        model = User
        fields = ["username", "email", "first_name", "last_name"]