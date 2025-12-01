import logging
from django.utils import timezone
from django.db.models import F
from django.db.models.functions import Greatest
from django.db import transaction
from django.http import JsonResponse

from Customers.models import Customer, LunchRecord, DinnerRecord

logger = logging.getLogger(__name__)
CONSUMING_SERVICES = ("DineIn", "PickUp", "Delivery")


def gen_Lunch_record(request=None):
    """
    Create missing lunch records for active users and decrement balances exactly once
    for today's consuming records.
    """
    today = timezone.localdate()
    customers_no_record = Customer.objects.filter(
        user_status_active=True,
        lunch_status_active=True
    ).exclude(lunch_records__for_date=today)

    logger.debug("gen_Lunch_record: customers without record count=%d", customers_no_record.count())

    lunch_records_to_create = []
    for c in customers_no_record:
        logger.debug("creating lunch record for: %s", c.email)
        lunch_records_to_create.append(
            LunchRecord(
                customer=c,
                for_date=today,
                meal_choice=c.default_meal_choice,
                meal_num_used=c.meal_balance,
                service_choice=c.default_service_choice,
                FLAGSHIP_choice=c.FLAGSHIP_MENU_LUNCH_default_choice,
                PREMIUM_choice=c.PREMIUM_MENU_LUNCH_default_choice
            )
        )

    created_count = 0

    try:
        with transaction.atomic():
            if lunch_records_to_create:
                # ignore_conflicts avoids race-duplicate errors if another worker created same record.
                LunchRecord.objects.bulk_create(lunch_records_to_create, ignore_conflicts=True)
                # Count how many were inserted - best effort:
                created_count = len(lunch_records_to_create)

            # Decrement customers who have today's lunch record with a consuming service and haven't been decremented yet.
            customers_to_decrement = Customer.objects.filter(
                lunch_records__for_date=today,
                lunch_records__service_choice__in=CONSUMING_SERVICES,
                lunch_records__decrement_done=False
            ).distinct()

            # Decrement meal_balance but not below 0
            customers_to_decrement.update(meal_balance=Greatest(F("meal_balance") - 1, 0))

            # Mark related LunchRecord(s) as decremented
            LunchRecord.objects.filter(
                for_date=today,
                service_choice__in=CONSUMING_SERVICES,
                decrement_done=False
            ).update(decrement_done=True)

            # Update low-balance flags and active status
            Customer.objects.filter(meal_balance__lte=6).update(low_balance_status_active=True)
            # if balance <= 0 consider inactive
            Customer.objects.filter(meal_balance__lte=0).update(user_status_active=False)

    except Exception as e:
        logger.exception("Unexpected error in gen_Lunch_record: %s", e)
        return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"created_count": created_count})


def gen_Dinner_record(request=None):
    """
    Mirror of gen_Lunch_record for dinner.
    """
    today = timezone.localdate()
    customers_no_record = Customer.objects.filter(
        user_status_active=True,
        dinner_status_active=True
    ).exclude(dinner_records__for_date=today)

    logger.debug("gen_Dinner_record: customers without record count=%d", customers_no_record.count())

    dinner_records_to_create = []
    for c in customers_no_record:
        logger.debug("creating dinner record for: %s", c.email)
        dinner_records_to_create.append(
            DinnerRecord(
                customer=c,
                for_date=today,
                meal_choice=c.default_meal_choice,
                meal_num_used=c.meal_balance,
                service_choice=c.default_service_choice,
                FLAGSHIP_choice=c.FLAGSHIP_MENU_DINNER_default_choice,
                PREMIUM_choice=c.PREMIUM_MENU_DINNER_default_choice
            )
        )

    created_count = 0

    try:
        with transaction.atomic():
            if dinner_records_to_create:
                DinnerRecord.objects.bulk_create(dinner_records_to_create, ignore_conflicts=True)
                created_count = len(dinner_records_to_create)

            customers_to_decrement = Customer.objects.filter(
                dinner_records__for_date=today,
                dinner_records__service_choice__in=CONSUMING_SERVICES,
                dinner_records__decrement_done=False
            ).distinct()

            customers_to_decrement.update(meal_balance=Greatest(F("meal_balance") - 1, 0))

            DinnerRecord.objects.filter(
                for_date=today,
                service_choice__in=CONSUMING_SERVICES,
                decrement_done=False
            ).update(decrement_done=True)

            Customer.objects.filter(meal_balance__lte=6).update(low_balance_status_active=True)
            Customer.objects.filter(meal_balance__lte=0).update(user_status_active=False)

    except Exception as e:
        logger.exception("Unexpected error in gen_Dinner_record: %s", e)
        return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"created_count": created_count})
