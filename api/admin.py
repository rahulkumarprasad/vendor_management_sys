from django.contrib import admin

from .models import *

# registering all tables
admin.site.register([Vendor, PurchaseOrder, HistoricalPerformance])