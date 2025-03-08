from django.contrib import admin
from .models import Profile, Category, Expense, Income, Budget, Resource, TransactionHistory, IncomeSource, BasicExpense, WishExpense, SavingsInvestment, Reminder


admin.site.register(Profile)
admin.site.register(Category)
admin.site.register(Expense)
admin.site.register(Income)
admin.site.register(Budget)
admin.site.register(Resource)
admin.site.register(TransactionHistory)
admin.site.register(IncomeSource)
admin.site.register(BasicExpense)
admin.site.register(WishExpense)
admin.site.register(SavingsInvestment)
admin.site.register(Reminder)

