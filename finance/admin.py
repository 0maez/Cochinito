from django.contrib import admin
from .models import Profile, Budget, Resource, IncomeSource, BasicExpense, WishExpense, SavingsInvestment, Transaction

# Registrar los modelos
admin.site.register(Profile)
admin.site.register(Budget)
admin.site.register(Resource)
admin.site.register(IncomeSource)
admin.site.register(BasicExpense)
admin.site.register(WishExpense)
admin.site.register(SavingsInvestment)
admin.site.register(Transaction)
