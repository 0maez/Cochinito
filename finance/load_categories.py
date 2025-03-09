import json
from finance.models import IncomeSource, BasicExpense, WishExpense, SavingsInvestment

def load_categories():
    with open('finance/fixtures/fixtures.json', 'r', encoding='utf-8') as file:
        categories = json.load(file)
    for category in categories:
        model = category['model']
        fields = category['fields']
        name = fields['name']
        if model == 'finance.IncomeSource':
            IncomeSource.objects.get_or_create(name=name)  
        elif model == 'finance.BasicExpense':
            BasicExpense.objects.get_or_create(name=name)  
        elif model == 'finance.WishExpense':
            WishExpense.objects.get_or_create(name=name) 
        elif model == 'finance.SavingsInvestment':
            SavingsInvestment.objects.get_or_create(name=name)  
    print("Categorías cargadas exitosamente.")
