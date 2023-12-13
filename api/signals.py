from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import PurchaseOrder, HistoricalPerformance
from django.db.models import Q, Count, Sum, DurationField, ExpressionWrapper, F
from datetime import timedelta

def get_total_hours_from_timedelta(time_delt_obj):
    """This function is used for converting timedelta object to hours
    :params:
        time_delt_obj: "time delta object"
    :return:
        float value representing total hours
    """
    return round(time_delt_obj.total_seconds()/(60*60),2)

@receiver(pre_save, sender=PurchaseOrder)
def update_metrics(sender, instance, **kwargs):
    """
    This function will be executed on each time with changes in PurchaseOrder model and the metrics data is calculated for only update query
    and it is used for calculating vendor metrics
    """
    # getting records from purchase order table for checking weather current instance model object is new object or updated object 
    try:
        previous = PurchaseOrder.objects.select_related("vendor").get(po_number=instance.po_number)
    except:
        previous = None

    if previous is not None: 
        #logic for handling update case
        vendor = previous.vendor

        try:
            #getting latest history data for the vendor
            latest_performance_history = HistoricalPerformance.objects.filter(vendor=vendor).order_by("-date").first()
        except:
            latest_performance_history = None

        #creating new history data for saving new details
        new_history_rec = HistoricalPerformance(vendor = vendor,
            on_time_delivery_rate = (latest_performance_history.on_time_delivery_rate if latest_performance_history else 0), 
            quality_rating_avg = (latest_performance_history.quality_rating_avg if latest_performance_history else 0), 
            average_response_time = (latest_performance_history.average_response_time if latest_performance_history else 0), 
            fulfillment_rate = (latest_performance_history.fulfillment_rate if latest_performance_history else 0),
            json_data = (latest_performance_history.json_data.copy() if latest_performance_history else {}))

        if previous.status != instance.status and instance.status == "completed":
            handel_on_time_delevery_rate(vendor, instance, latest_performance_history, new_history_rec)

        if previous.quality_rating != instance.quality_rating and instance.status == "completed":
            handel_quality_rate_average(instance, vendor, latest_performance_history, new_history_rec)
            
        if previous.acknowledgment_date != instance.acknowledgment_date:
            handel_average_response_time(instance, vendor, latest_performance_history, new_history_rec)
        
        if previous.status != instance.status:
            handel_fulfilment_rate(instance, vendor, latest_performance_history, new_history_rec)
        
        #saving new details
        vendor.save()
        new_history_rec.save()

def handel_on_time_delevery_rate(vendor, instance, latest_performance_history, new_history_rec):
    """
    This is calculated each time a PO status changes to 'completed
    :params:
        vendor: "current vendor object"
        instance: "current instance or purchase order model"
        latest_performance_history: "latest object record from historical performance model"
        new_history_rec: "new object of historical performance model"
    """
    #logic for handlaing On-Time Delivery Rate
    if latest_performance_history:

        on_time_completed_count = PurchaseOrder.objects.filter(Q(vendor=vendor) & Q(status="completed") & 
                    Q(delivery_date__lte = F("expected_delivery_date")) &
                        ~Q(po_number=instance.po_number) & Q(modified_date__gt=latest_performance_history.date)).count()
        on_time_total_completed_order = PurchaseOrder.objects.filter(Q(vendor=vendor) & Q(status="completed") & 
                        ~Q(po_number=instance.po_number) & Q(modified_date__gt=latest_performance_history.date)).count()
        
        if "on_time_completed_count" in latest_performance_history.json_data:
            on_time_completed_count += latest_performance_history.json_data["on_time_completed_count"]
        
        if "on_time_total_completed_order" in latest_performance_history.json_data:
            on_time_total_completed_order += latest_performance_history.json_data["on_time_total_completed_order"]

    else:
        on_time_completed_count = PurchaseOrder.objects.filter(Q(vendor=vendor) & Q(status="completed") & Q(delivery_date__lte = F("expected_delivery_date")) & ~Q(po_number=instance.po_number)).count()
        on_time_total_completed_order = PurchaseOrder.objects.filter(Q(vendor=vendor) & Q(status="completed") & ~Q(po_number=instance.po_number)).count()

    if instance.status == "completed":
        on_time_total_completed_order += 1

    if instance.delivery_date and instance.delivery_date <= instance.expected_delivery_date:
        on_time_completed_count += 1

    if on_time_total_completed_order != 0:
        result = round(on_time_completed_count/on_time_total_completed_order,2)
        vendor.on_time_delivery_rate = result
        
        new_history_rec.json_data["on_time_completed_count"] = on_time_completed_count
        new_history_rec.json_data["on_time_total_completed_order"] = on_time_total_completed_order
        new_history_rec.on_time_delivery_rate = result

def handel_quality_rate_average(instance, vendor, latest_performance_history, new_history_rec):
    """
    This is calculated upon the completion of each PO where a quality_rating is provided
    :params:
        vendor: "current vendor object"
        instance: "current instance or purchase order model"
        latest_performance_history: "latest object record from historical performance model"
        new_history_rec: "new object of historical performance model"
    """
    #logic for handlaing Quality Rating Average
    if latest_performance_history:
        query_res = PurchaseOrder.objects.filter(Q(vendor=vendor) & Q(status="completed") &
                    ~Q(quality_rating=None) & ~Q(po_number=instance.po_number) & 
                    Q(modified_date__gt=latest_performance_history.date)).aggregate(Sum("quality_rating"),
                                                    Count("quality_rating"))
        
        if query_res["quality_rating__sum"]:
            qtn_rate_avg_sum_of_all = query_res["quality_rating__sum"] + instance.quality_rating
        else:
            qtn_rate_avg_sum_of_all = 0 + instance.quality_rating

        qtn_rate_avg_total_count = query_res["quality_rating__count"] + 1

        if "qtn_rate_avg_sum_of_all" in latest_performance_history.json_data:
            qtn_rate_avg_sum_of_all += latest_performance_history.json_data["qtn_rate_avg_sum_of_all"]
        if "qtn_rate_avg_total_count" in latest_performance_history.json_data:
            qtn_rate_avg_total_count += latest_performance_history.json_data["qtn_rate_avg_total_count"]
    
    else:
        query_res = PurchaseOrder.objects.filter(Q(vendor=vendor) & Q(status="completed") &
                    ~Q(quality_rating=None) & ~Q(po_number=instance.po_number)).aggregate(Sum("quality_rating"),
                                                    Count("quality_rating"))
        if query_res["quality_rating__sum"]:
            qtn_rate_avg_sum_of_all = query_res["quality_rating__sum"] + instance.quality_rating
        else:
            qtn_rate_avg_sum_of_all = 0 + instance.quality_rating

        qtn_rate_avg_total_count = query_res["quality_rating__count"] + 1

    avrage = round(qtn_rate_avg_sum_of_all/qtn_rate_avg_total_count,2)
    vendor.quality_rating_avg = avrage
    new_history_rec.json_data["qtn_rate_avg_sum_of_all"] = qtn_rate_avg_sum_of_all
    new_history_rec.json_data["qtn_rate_avg_total_count"] = qtn_rate_avg_total_count
    new_history_rec.quality_rating_avg = avrage


def handel_average_response_time(instance, vendor, latest_performance_history, new_history_rec):
    """
    This is calculated each time a PO is acknowledged by the vendor.
    :params:
        vendor: "current vendor object"
        instance: "current instance or purchase order model"
        latest_performance_history: "latest object record from historical performance model"
        new_history_rec: "new object of historical performance model"
    """
    #logic for handlaing Average Response Time
    #null values will be ignored
    if latest_performance_history:
        query_res = PurchaseOrder.objects.filter(Q(vendor=vendor) & ~Q(po_number=instance.po_number)
                        & Q(modified_date__gt=latest_performance_history.date)).annotate(
            diff = ExpressionWrapper(F("acknowledgment_date")-F("issue_date"), output_field = DurationField())
        ).aggregate(Count("diff"),Sum("diff"))
        
        avrage_response_time_sum_of_all = query_res["diff__sum"]
        avrage_response_time_total_count = query_res["diff__count"]

        if not avrage_response_time_sum_of_all:
            avrage_response_time_sum_of_all = timedelta(seconds=0)

        if "avrage_response_time_sum_of_all" in latest_performance_history.json_data:
            avrage_response_time_sum_of_all += timedelta(hours = latest_performance_history.json_data["avrage_response_time_sum_of_all"])
        
        if "avrage_response_time_total_count" in latest_performance_history.json_data:
            avrage_response_time_total_count += latest_performance_history.json_data["avrage_response_time_total_count"]

    else:
        query_res = PurchaseOrder.objects.filter(Q(vendor=vendor) & ~Q(po_number=instance.po_number)).annotate(
            diff = ExpressionWrapper(F("acknowledgment_date")-F("issue_date"), output_field = DurationField())
        ).aggregate(Count("diff"),Sum("diff"))
        avrage_response_time_sum_of_all = query_res["diff__sum"]
        avrage_response_time_total_count = query_res["diff__count"]
        
        if not avrage_response_time_sum_of_all:
            avrage_response_time_sum_of_all = timedelta(seconds=0)

    if instance.acknowledgment_date:
        curent_obj_diff = instance.acknowledgment_date - instance.issue_date
        avrage_response_time_sum_of_all+=curent_obj_diff
        avrage_response_time_total_count += 1
    
    avrage_response_time = avrage_response_time_sum_of_all/avrage_response_time_total_count
    total_hours = get_total_hours_from_timedelta(avrage_response_time)
    vendor.average_response_time = total_hours
    new_history_rec.json_data["avrage_response_time_sum_of_all"] = get_total_hours_from_timedelta(avrage_response_time_sum_of_all)
    new_history_rec.json_data["avrage_response_time_total_count"] = avrage_response_time_total_count
    new_history_rec.average_response_time = total_hours

def handel_fulfilment_rate(instance, vendor, latest_performance_history, new_history_rec):
    """
    This is calculated upon any change in PO status.
    :params:
        vendor: "current vendor object"
        instance: "current instance or purchase order model"
        latest_performance_history: "latest object record from historical performance model"
        new_history_rec: "new object of historical performance model"
    """
    #logic for handlaing Fulfilment Rate
    #adding one for current order
    if latest_performance_history:

        fullfilment_rate_total_orders = PurchaseOrder.objects.filter(Q(vendor=vendor) & ~Q(po_number=instance.po_number) 
                                & Q(modified_date__gt=latest_performance_history.date)).count() + 1
        fullfilment_rate_total_completed_order = PurchaseOrder.objects.filter(Q(vendor=vendor) & Q(status="completed") & 
                                ~Q(po_number=instance.po_number)
                                & Q(modified_date__gt=latest_performance_history.date)).count()

        if "fullfilment_rate_total_orders" in latest_performance_history.json_data:
            fullfilment_rate_total_orders += latest_performance_history.json_data["fullfilment_rate_total_orders"]

        if "fullfilment_rate_total_completed_order" in latest_performance_history.json_data:
            fullfilment_rate_total_completed_order += latest_performance_history.json_data["fullfilment_rate_total_completed_order"]

    else:
        fullfilment_rate_total_orders = PurchaseOrder.objects.filter(Q(vendor=vendor) & ~Q(po_number=instance.po_number)).count() + 1
        fullfilment_rate_total_completed_order = PurchaseOrder.objects.filter(Q(vendor=vendor) & Q(status="completed") & ~Q(po_number=instance.po_number)).count()

    if instance.status == "completed":
        fullfilment_rate_total_completed_order += 1

    if fullfilment_rate_total_orders != 0:
        result = round(fullfilment_rate_total_completed_order/fullfilment_rate_total_orders,2)
        vendor.fulfillment_rate = result
        new_history_rec.json_data["fullfilment_rate_total_orders"] = fullfilment_rate_total_orders
        new_history_rec.json_data["fullfilment_rate_total_completed_order"] = fullfilment_rate_total_completed_order
        new_history_rec.fulfillment_rate = result