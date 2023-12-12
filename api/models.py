from django.db import models
import uuid
import random

def create_new_odr_number():
      return str(random.randint(1000000000, 9999999999))

class Vendor(models.Model):
    vendor_code = models.CharField(primary_key=True, unique=True, max_length=36, default=uuid.uuid4)
    name = models.CharField(max_length = 200)
    contact_details = models.TextField()
    address = models.TextField()
    on_time_delivery_rate = models.FloatField(default=0)
    quality_rating_avg = models.FloatField(default=0)
    average_response_time = models.FloatField(default=0)
    fulfillment_rate = models.FloatField(default=0)
    
    def __str__(self):
         return f"{self.name}: ({self.vendor_code})"

class PurchaseOrder(models.Model):
    STATUS_CONSTANTS = [("pending","pending"),("completed","completed"),("canceled","canceled")]
    po_number = models.CharField(primary_key=True, max_length=10, unique=True, default=create_new_odr_number)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add = True)
    delivery_date = models.DateTimeField(null=True, blank=True)
    expected_delivery_date = models.DateTimeField()
    items = models.JSONField()
    quantity = models.IntegerField()
    status = models.CharField(max_length=20, default="pending", choices=STATUS_CONSTANTS) #["pending", "completed", "canceled"]
    quality_rating = models.FloatField(null=True, blank=True)
    issue_date = models.DateTimeField(auto_now_add = True)
    acknowledgment_date = models.DateTimeField(null=True, blank=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
         return f"{self.vendor.name}: ({self.po_number})"

class HistoricalPerformance(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    on_time_delivery_rate = models.FloatField()
    quality_rating_avg = models.FloatField()
    average_response_time = models.FloatField()
    fulfillment_rate = models.FloatField()
    json_data = models.JSONField()