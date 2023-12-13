from drf_yasg import openapi

# decalearing schema for performasce API sagger response
VENDOR_SCHEMA = {
"vendor_code":{"type":"string",
        "title": "Vendor code",
        "readOnly": True},
"name":	{"type":"string",
        "title": "Name",
        "readOnly": True},
"on_time_delivery_rate":{"type":"number",
        "title": "On time delivery rate",
        "readOnly": True,},
"quality_rating_avg": {"type":"number",
        "title": "Quality rating avg",
        "readOnly": True,},
"average_response_time":{"type":"number",
        "title": "Average response time in hours",
        "readOnly": True,},
"fulfillment_rate":{"type":"number",
        "title": "Fulfillment rate",
        "readOnly": True,}
}

VendorPerformanceSchema = openapi.Response(
        description="200 response",
        examples={
            "application/json": VENDOR_SCHEMA
        }
    )