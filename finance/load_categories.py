import json
from django.contrib.auth.models import User
from finance.models import IncomeSource, BasicExpense, WishExpense, SavingsInvestment

def load_categories(user):
    with open('finance/fixtures/fixtures.json', 'r', encoding='utf-8') as file:
        categories = json.load(file)
    for category in categories:
        model = category['model']
        fields = category['fields']
        if model == 'finance.IncomeSource':
            IncomeSource.objects.get_or_create(user=user, name=fields['name'])
        elif model == 'finance.BasicExpense':
            BasicExpense.objects.get_or_create(user=user, name=fields['name'])
        elif model == 'finance.WishExpense':
            WishExpense.objects.get_or_create(user=user, name=fields['name'])
        elif model == 'finance.SavingsInvestment':
            SavingsInvestment.objects.get_or_create(user=user, name=fields['name'])
    print(f"Categorías cargadas exitosamente para el usuario {user.username}.")