from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .serializers import *
from .models import Vendor, PurchaseOrder
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.mixins import UpdateModelMixin
from rest_framework.generics import GenericAPIView
from drf_yasg.utils import swagger_auto_schema
from django.utils.decorators import method_decorator
from .response_schema import VendorPerformanceSchema

class VendorViewSet(ModelViewSet):
    """
    This Vendor view set is used for CRUD operation on Vendor data"""
    serializer_class = VendorSerializer
    queryset = Vendor.objects.all()

class PurchaseOrderViewSet(ModelViewSet):
    """This model view set is used for CRUD operation on PurchaseOrder data"""
    serializer_class = PurchaseOrderSerializer
    queryset = PurchaseOrder.objects.all()

@method_decorator(name="get",decorator=swagger_auto_schema(
    responses={200: VendorPerformanceSchema}
))
class VendorPerformance(APIView):
    """This API view is used for Getting metric data of Vendor"""
    def get(self, request, vendor_id, format=None):
        try:
            obj = Vendor.objects.get(vendor_code=vendor_id)
            ser = VendorPerformanceSerializer(obj)
            return Response(ser.data)

        except Vendor.DoesNotExist as e:
            return Response({"error":f"User does not exist"}, status=404)

        except Exception as e:
            return Response({"error":f"Exception occured, message: {e}"}, status=500)

class PurchaseOrderAck(UpdateModelMixin, GenericAPIView):
    """This view is used for updating acknowledge date of PurchaseOrder"""
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderUpdateSerializer

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)