from django.contrib import admin

from .models import *

admin.site.register([Vendor, PurchaseOrder, HistoricalPerformance])