from django.contrib import admin
from .models import Profile, Budget, Resource, IncomeSource, BasicExpense, WishExpense, SavingsInvestment, Reminder, Transaction, Module, BasicTerm

admin.site.register(Profile)
admin.site.register(Budget)
admin.site.register(Resource)
admin.site.register(IncomeSource)
admin.site.register(BasicExpense)
admin.site.register(WishExpense)
admin.site.register(SavingsInvestment)
admin.site.register(Reminder)
admin.site.register(Transaction)
admin.site.register(Module)
admin.site.register(BasicTerm)

