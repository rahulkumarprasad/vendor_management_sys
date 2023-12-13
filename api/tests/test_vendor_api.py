import pytest
from api.models import *
from api.tests.test_purchaseorder_api import get_token, client

@pytest.mark.django_db
class TestVendorApi:
    """
    This class is created for testing API's related to vendor
    """
    client = client
    vendor_url = "/api/vendors/"

    def create_vendor(self):
        """
        This method will create new vendor in database
        """
        vendor = Vendor(name="test",contact_details="87123656123", address="test address")
        vendor.save()
        return vendor

    def test_get_vendors(self):
        """
        This method will test get vendors api
        """
        token = get_token()
        response = self.client.get(self.vendor_url, headers={"Authorization":f"Bearer {token}"})
        assert response.status_code == 200

    def test_get_vendor_detail(self):
        """
        This method will test get vendor details api
        """
        token = get_token()
        vendor = self.create_vendor()

        response = self.client.get(self.vendor_url + f"{vendor.pk}/", headers={"Authorization":f"Bearer {token}"})
        assert response.status_code == 200

    def test_post_vendor(self):
        """
        This method will test post vendor api
        """
        token = get_token()
        body = {
            "name": "new test vendor",
            "contact_details": "76123871281",
            "address": "sikkim"
            }

        response = self.client.post(self.vendor_url , data = body, 
                                    content_type="application/json",  headers={"Authorization":f"Bearer {token}"})
        assert response.status_code == 201

    def test_put_vendor(self):
        """
        This method will test put vendor api
        """
        token = get_token()
        vendor = self.create_vendor()
        body = {
            "name": "new test vendor updated",
            "contact_details": "7661367717182",
            "address": "gangtok"
            }

        response = self.client.put(self.vendor_url + f"{vendor.pk}/" , data = body, 
                                    content_type="application/json",  headers={"Authorization":f"Bearer {token}"})
        assert response.status_code == 200

    def test_delete_vendor(self):
        """
        This method will test delete vendor api
        """
        token = get_token()
        vendor = self.create_vendor()
        response = self.client.delete(self.vendor_url + f"{vendor.pk}/" , headers={"Authorization":f"Bearer {token}"})
        assert response.status_code == 204
    
    def test_get_vendor_performance(self):
        """
        This method will test get vendor performance api
        """
        token = get_token()
        order = self.create_vendor()
        response = self.client.get(self.vendor_url + f"{order.pk}/performance" , headers={"Authorization":f"Bearer {token}"})
        assert response.status_code == 200