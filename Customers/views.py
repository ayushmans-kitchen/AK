from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
import json

from .models import Customer,LunchRecord,DinnerRecord

@login_required
def user_dashboard(request):
    user=request.user
    
    used_meals= user.total_meals - user.meal_balance
    cl_l=LunchRecord.objects.filter(service_choice="Cancel",customer=user).count()
    cl_d=DinnerRecord.objects.filter(service_choice="Cancel",customer=user).count()
    cancelled_meals=cl_l+cl_d
    context={
        'user':user,
        'used_meals':used_meals,
        'cancelled_meals':cancelled_meals
        }
    return render(request, 'Customer/user-dashboard.html',context)


@login_required
@require_POST
def api_meal_selection(request):

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return HttpResponseBadRequest("Invalid JSON")

    meal_type = payload.get('meal_type')
    service = payload.get('service')
    food = payload.get('food')  # can be None

    if meal_type not in ('lunch', 'dinner') or service not in ('dining', 'pickup', 'delivery', 'cancel'):
        return JsonResponse({'success': False, 'message': 'Invalid payload'}, status=400)

    # TODO: Replace below with real DB logic.
    # For demo: update the static MEAL_PLANS dict (not persistent).
    plan_key = getattr(request.user, 'customer_plan_key', 'premium2_60')
    plan = MEAL_PLANS.get(plan_key)
    if not plan:
        return JsonResponse({'success': False, 'message': 'Plan not found'}, status=404)

    # Simulate business logic:
    # - If service == 'cancel' => increment cancelledMeals by 1 (and maybe decrement used)
    # - Else => increment usedMeals by 1
    if service == 'cancel':
        plan['cancelledMeals'] = plan.get('cancelledMeals', 0) + 1
    else:
        # simple check: cannot use more than total (optional)
        if plan.get('usedMeals', 0) + 1 > plan.get('totalMeals', 0):
            return JsonResponse({'success': False, 'message': 'Not enough meals available'}, status=400)
        plan['usedMeals'] = plan.get('usedMeals', 0) + 1

    # recompute available using same formula (total - used + cancelled)
    available = plan['totalMeals'] - plan['usedMeals'] + plan['cancelledMeals']

    # In real app: create a LunchRecord/DinnerRecord instance with user, meal_type, service, food, for_date=timezone.localdate()
    # and persist in DB. Use transactions to ensure consistency.

    return JsonResponse({
        'success': True,
        'message': f"{meal_type.title()} processed: {service}{' - ' + food if food else ''}",
        'updated_counters': {
            'used': plan['usedMeals'],
            'cancelled': plan['cancelledMeals'],
            'available': available,
        }
    })

def user_history(request):
    return render(request,"Customer/user-history.html")