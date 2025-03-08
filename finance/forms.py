from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from finance.models import Profile, IncomeSource, BasicExpense, WishExpense, SavingsInvestment, Transaction, Budget


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
        queryset=IncomeSource.objects.none(),  
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None) 
        super().__init__(*args, **kwargs)
        if user:
            self.fields['income_sources'].queryset = IncomeSource.objects.filter(user=user)

    def save(self, user):
        income_sources = self.cleaned_data['income_sources']
        for source in income_sources:
            IncomeSource.objects.get_or_create(user=user, name=source.name)
    
class BasicExpenseForm(forms.Form):
    basic_expenses = forms.ModelMultipleChoiceField(
        queryset=BasicExpense.objects.none(),  
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  
        super().__init__(*args, **kwargs)
        if user:
            
            self.fields['basic_expenses'].queryset = BasicExpense.objects.filter(user=user)

    def save(self, user):
        basic_expenses = self.cleaned_data['basic_expenses']
        for expense in basic_expenses:
            BasicExpense.objects.get_or_create(user=user, name=expense.name)

class WishExpenseForm(forms.Form):
    wish_expenses = forms.ModelMultipleChoiceField(
        queryset=WishExpense.objects.none(),  
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  
        super().__init__(*args, **kwargs)
        if user:
            self.fields['wish_expenses'].queryset = WishExpense.objects.filter(user=user)

    def save(self, user):
        wish_expenses = self.cleaned_data['wish_expenses']
        for wish in wish_expenses:
            WishExpense.objects.get_or_create(user=user, name=wish.name)

class SavingsInvestmentForm(forms.Form):
    savings_investments = forms.ModelMultipleChoiceField(
        queryset=SavingsInvestment.objects.none(),  
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  
        super().__init__(*args, **kwargs)
        if user:
            self.fields['savings_investments'].queryset = SavingsInvestment.objects.filter(user=user)

    def save(self, user):
        savings_investments = self.cleaned_data['savings_investments']
        for saving in savings_investments:
            SavingsInvestment.objects.get_or_create(user=user, name=saving.name)

class ProfileForm(forms.ModelForm):
    class Meta: 
        model = User
        fields = ["username", "email", "first_name", "last_name"]

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['total_amount']  

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['total_amount'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Ingresa tu presupuesto inicial'})
        
class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['name', 'amount', 'description', 'category', 'income_source', 'basic_expense', 'wish_expense', 'savings_investment']

    def __init__(self, *args, **kwargs):
        self.transaction_type = kwargs.pop('transaction_type', None)  
        user = kwargs.pop('user', None) 
        super().__init__(*args, **kwargs)
        if self.transaction_type == 'income':
            self.fields['income_source'].queryset = IncomeSource.objects.filter(user=user)
            self.fields['basic_expense'].widget = forms.HiddenInput()  
            self.fields['wish_expense'].widget = forms.HiddenInput() 
            self.fields['savings_investment'].widget = forms.HiddenInput()  
        elif self.transaction_type == 'expense':
            self.fields['basic_expense'].queryset = BasicExpense.objects.filter(user=user)
            self.fields['wish_expense'].queryset = WishExpense.objects.filter(user=user)
            self.fields['income_source'].widget = forms.HiddenInput()  
            self.fields['savings_investment'].widget = forms.HiddenInput()  
