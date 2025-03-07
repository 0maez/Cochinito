from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, IncomeSource, BasicExpense, WishExpense, SavingsInvestment, Reminder, Budget



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

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['total_amount']  # Solo necesitamos el campo total_amount por ahora

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['total_amount'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Ingresa tu presupuesto inicial'})

class ReminderForm(forms.ModelForm):
    class Meta:
        model = Reminder
        fields = ['name', 'description', 'amount', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
        }