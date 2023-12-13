import pytest
from api.models import *
from django.contrib.auth.models import User
from django.urls import reverse
from django.test.client import Client
from datetime import datetime

client = Client()

@pytest.mark.django_db
def create_user():
    """
    This function will create new user in test database
    """
    User.objects.create_user("admin", "admin@admin.com", "admin")
    
def get_token():
    """
    This function will generate token for new user
    """
    create_user()
    response = client.post(reverse("token_obtain_pair"), 
                            data={"username":"admin", "password":"admin"}, 
                            content_type="application/json")
    return response.json()["access"]

@pytest.mark.django_db
class TestOrderApi:
    """
    This class is created for testing API's related to purchase orders
    """

    client = client
    purchase_order_url_path = "/api/purchase_orders/"

    def create_vendor(self):
        """
        This method will create new vendor in database
        """
        vendor = Vendor(name="test",contact_details="87123656123", address="test address")
        vendor.save()
        return vendor
    
    def create_purchase_order(self):
        """
        This method will create new purchase order in database
        """
        vendor = self.create_vendor()
        order = PurchaseOrder(vendor=vendor, 
                              expected_delivery_date=datetime.now(),
                              items={"test":"test item"}, 
                              quantity=1,
                              status="pending",
                              )
        order.save()
        return order

    def test_get_purchase_order(self):
        """
        This method will test get purchase orders api
        """
        token = get_token()
        response = self.client.get(self.purchase_order_url_path, headers={"Authorization":f"Bearer {token}"})
        assert response.status_code == 200

    def test_get_purchase_order_for_id(self):
        """
        This method will test get purchase orders detail api
        """
        token = get_token()
        order = self.create_purchase_order()

        response = self.client.get(self.purchase_order_url_path + f"{order.po_number}/", headers={"Authorization":f"Bearer {token}"})
        assert response.status_code == 200

    def test_post_purchase_order(self):
        """
        This method will test post purchase orders api
        """
        token = get_token()
        vendor = self.create_vendor()
        body = {
            "vendor": vendor.pk,
            "delivery_date": "2023-12-12T16:52:41.061Z",
            "expected_delivery_date": "2023-12-12T16:52:41.061Z",
            "items": {
                "item1": {
                    "qtn": 2
                },
                "item2": {
                    "qtn": 10
                }
                },
            "quantity": 2,
            "status": "pending",
            "quality_rating": 0,
            "acknowledgment_date": "2023-12-12T16:52:41.061Z"
            }

        response = self.client.post(self.purchase_order_url_path , data = body, 
                                    content_type="application/json",  headers={"Authorization":f"Bearer {token}"})
        assert response.status_code == 201

    def test_put_purchase_order(self):
        """
        This method will test put purchase orders api
        """
        token = get_token()
        order = self.create_purchase_order()
        body = {
            "vendor": order.vendor.pk,
            "delivery_date": "2023-12-13T02:04:32.322Z",
            "expected_delivery_date": "2023-12-13T02:04:32.322Z",
            "items": {"test":"test item"},
            "quantity": 1,
            "status": "pending",
            "quality_rating": 0,
            "acknowledgment_date": "2023-12-13T02:04:32.322Z"
            }

        response = self.client.put(self.purchase_order_url_path + f"{order.pk}/" , data = body, 
                                    content_type="application/json",  headers={"Authorization":f"Bearer {token}"})
        assert response.status_code == 200

    def test_delete_purchase_order(self):
        """
        This method will test delete purchase orders api
        """
        token = get_token()
        order = self.create_purchase_order()
        response = self.client.delete(self.purchase_order_url_path + f"{order.pk}/" , headers={"Authorization":f"Bearer {token}"})
        assert response.status_code == 204
    
    def test_acknowledge_purchase_order(self):
        """
        This method will test acknowledge purchase orders api
        """
        token = get_token()
        order = self.create_purchase_order()
        body = {
            "acknowledgment_date": "2023-12-16T02:12:19.839Z"
            }
        response = self.client.put(self.purchase_order_url_path + f"{order.pk}/acknowledge" , data = body, 
                                    content_type="application/json",  headers={"Authorization":f"Bearer {token}"})
        assert response.status_code == 200
