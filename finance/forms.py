from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, IncomeSource, BasicExpense, WishExpense, SavingsInvestment, Reminder, Budget
from django.contrib.auth.forms import UserChangeForm
from finance.models import Profile, IncomeSource, BasicExpense, WishExpense, SavingsInvestment, Transaction, Budget


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    age = forms.IntegerField(required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "age", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

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
        queryset=IncomeSource.objects.filter(user__isnull=True),  # Mostrar todas las categorías
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # No necesitas el argumento 'user'

    
class BasicExpenseForm(forms.Form):
    basic_expenses = forms.ModelMultipleChoiceField(
        queryset=BasicExpense.objects.filter(user__isnull=True),  
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class WishExpenseForm(forms.Form):
    wish_expenses = forms.ModelMultipleChoiceField(
        queryset=WishExpense.objects.filter(user__isnull=True),  
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class SavingsInvestmentForm(forms.Form):
    savings_investments = forms.ModelMultipleChoiceField(
        queryset=SavingsInvestment.objects.filter(user__isnull=True),  
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ProfileForm(forms.ModelForm):
    class Meta: 
        model = User
        fields = ["username", "email", "first_name", "last_name"]

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['total_amount']
        labels = {
            'total_amount': 'Presupuesto inicial',  
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['total_amount'].widget.attrs.update({
            'class': 'form-control border-2 border-[#4b7f8c] rounded-lg p-2 w-full',
            'placeholder': 'Ingresa tu presupuesto inicial'
        })

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
        
class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['name', 'amount', 'description', 'income_source', 'basic_expense', 'wish_expense', 'savings_investment']

    def __init__(self, *args, **kwargs):
        self.transaction_type = kwargs.pop('transaction_type', None)  
        user = kwargs.pop('user', None) 
        super().__init__(*args, **kwargs)
        if self.transaction_type == 'income':
            self.fields['income_source'].queryset = IncomeSource.objects.filter(user__isnull=True)
            self.fields['basic_expense'].widget = forms.HiddenInput()  
            self.fields['wish_expense'].widget = forms.HiddenInput() 
            self.fields['savings_investment'].widget = forms.HiddenInput()  
        elif self.transaction_type == 'expense':
            self.fields['basic_expense'].queryset = BasicExpense.objects.filter(user__isnull=True)
            self.fields['wish_expense'].queryset = WishExpense.objects.filter(user__isnull=True)
            self.fields['income_source'].widget = forms.HiddenInput()  
            self.fields['savings_investment'].widget = forms.HiddenInput()
        elif self.transaction_type == 'savings':
            self.fields['savings_investment'].queryset = SavingsInvestment.objects.filter(user__isnull=True)
            self.fields['income_source'].widget = forms.HiddenInput()
            self.fields['basic_expense'].widget = forms.HiddenInput()
            self.fields['wish_expense'].widget = forms.HiddenInput()  

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['age']