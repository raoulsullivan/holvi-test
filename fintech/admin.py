from django.contrib import admin, messages
from django.shortcuts import redirect
from .models import Account, Transaction
from .errors import AccountBalanceError

class TransactionInline(admin.TabularInline):
    model = Transaction
    fields = ('uuid', 'transaction_date', 'amount', 'description', 'active')
    ordering = ('-create_time', '-transaction_date')
    readonly_fields = fields
    can_delete = False
    show_change_link = True

    def get_extra(self, request, obj=None, **kwargs):
        return 0

    def has_add_permission(self, request, obj=None):
        return False

class AccountAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'name', 'user', 'balance')
    inlines = (TransactionInline,)
    search_fields = ('name', 'user__username')
    readonly_fields = ('uuid', 'user', 'balance',)

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'description', 'transaction_date', 'account')
    readonly_fields = ('uuid',)
    search_fields = ('description', 'account__name', 'account__user__username')
    list_filter = ['transaction_date']
    ordering = ('-transaction_date', '-create_time')

    def save_model(self, request, obj, form, change):
        try:
            super().save_model(request, obj, form, change)
        except AccountBalanceError as err:
            messages.error(request, err)
            return redirect('admin:fintech_transaction_changelist')

    def delete_model(self, request, obj):
        try:
            super().delete_model(request, obj)
        except AccountBalanceError as err:
            messages.error(request, err)
            return redirect('admin:fintech_transaction_changelist')

admin.site.register(Account, AccountAdmin)
admin.site.register(Transaction, TransactionAdmin)
