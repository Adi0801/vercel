from django.contrib import admin
from ecommerceapp.models import Contact,Products,Orders,OrderUpdate
# Register your models here.
admin.site.register(Contact)
admin.site.register(Products)
admin.site.register(Orders)
admin.site.register(OrderUpdate)