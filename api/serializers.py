from rest_framework import serializers
from .models import Vendor, PurchaseOrder
from rest_framework.reverse import reverse
from django.conf import settings

class ParameterisedHyperlinkedIdentityField(serializers.HyperlinkedIdentityField):
    """
    This class is used for creating url for performance of a vendor.
    lookup_fields is a tuple of tuples of the form:
        ('model_field', 'url_parameter')
    """
    lookup_fields = (('pk', 'pk'),)

    def __init__(self, *args, **kwargs):
        self.lookup_fields = kwargs.pop('lookup_fields', self.lookup_fields)
        super(ParameterisedHyperlinkedIdentityField, self).__init__(*args, **kwargs)

    def get_url(self, obj, view_name, request, format):
        """
        Given an object, return the URL that hyperlinks to the object.
        """
        kwargs = {}
        for model_field, url_param in self.lookup_fields:
            attr = obj
            for field in model_field.split('.'):
                attr = getattr(attr,field)
            kwargs[url_param] = attr

        return reverse(view_name, kwargs=kwargs, request=request, format=format)

class VendorSerializer(serializers.ModelSerializer):
    """
    This class is model serializer for converting vendor model object to json data
    its used for converting vendor data to json data
    """
    vendor_code = serializers.CharField(read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name='vendor-detail', read_only=True)
    performance_url = ParameterisedHyperlinkedIdentityField(view_name='vendors_performance', lookup_fields = (("vendor_code","vendor_id"),), read_only=True)
    class Meta:
        model = Vendor
        fields = ["vendor_code", "url", "performance_url", "name", "contact_details", "address", "on_time_delivery_rate", 
                  "quality_rating_avg", "average_response_time", "fulfillment_rate"]
        
class PurchaseOrderSerializer(serializers.ModelSerializer):
    """
    This class is model serializer for converting purchase order model object to json data
    its used to convert purchace order data to json
    """
    po_number = serializers.CharField(read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name='purchaseorder-detail', read_only=True)
    acknowledge_url = ParameterisedHyperlinkedIdentityField(view_name='purchase_order_ack', read_only=True)
    class Meta:
        model = PurchaseOrder
        fields = ["po_number", "url", "acknowledge_url", "vendor", "order_date", "delivery_date", "expected_delivery_date", "items", 
                  "quantity", "status", "quality_rating", "issue_date", "acknowledgment_date"]
    
    def validate_quality_rating(self, value):
        """Adding custom validaton"""
        if value != None and value > settings.DEFAULT_QUALITY_RATING_MAX_VALUE:
            raise serializers.ValidationError("maximum rating value is 10")
        return value

class VendorPerformanceSerializer(serializers.ModelSerializer):
    """
    This class is model serializer for converting vendor performance model data object to json data
    its used for converting metric data of vendor to json
    """
    vendor_code = serializers.CharField(read_only=True)
    class Meta:
        model = Vendor
        fields = ["vendor_code", "name", "on_time_delivery_rate", 
                  "quality_rating_avg", "average_response_time", "fulfillment_rate"]
        
class PurchaseOrderUpdateSerializer(serializers.ModelSerializer):
    """
    This class is model serializer for converting acknowledgment date from json to model object
    its used for converting purchace acknowledge data into json
    """
    po_number = serializers.CharField(read_only=True)
    class Meta:
        model = PurchaseOrder
        fields = ["po_number", "acknowledgment_date"]