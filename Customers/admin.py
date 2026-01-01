from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Customer, LunchRecord, DinnerRecord


@admin.register(Customer)
class CustomerAdmin(UserAdmin):
    model = Customer

    # =========================
    # LIST PAGE
    # =========================
    list_display = (
        "email",
        "name",
        "subscription_choice",
        "meal_balance",
        "user_status_active",
        "lunch_status_active",
        "dinner_status_active",
        "paused_subscription",
        "is_active",
        "is_staff",
    )

    list_filter = (
        "subscription_choice",
        "paused_subscription",
        "user_status_active",
        "lunch_status_active",
        "dinner_status_active",
        "is_active",
        "is_staff",
    )

    search_fields = ("email", "name", "phone")
    ordering = ("email",)

    # =========================
    # DETAIL / EDIT PAGE
    # =========================
    fieldsets = (
        (None, {
            "fields": ("email", "password")
        }),

        ("Personal Information", {
            "fields": (
                "name",
                "phone",
                "address",
            )
        }),

        ("Subscription Details", {
            "fields": (
                "subscription_choice",
                "subscription_phase",
                "meal_balance",
                "paused_subscription",
            )
        }),

        ("Default Meal Preferences", {
            "fields": (
                "default_lunch_service_choice",
                "default_dinner_service_choice",
                "default_meal_choice",
                "default_sunday_choice",
            )
        }),

        ("Flagship Defaults", {
            "fields": (
                "FLAGSHIP_MENU_LUNCH_default_choice",
                "FLAGSHIP_MENU_DINNER_default_choice",
            )
        }),

        ("Premium Defaults", {
            "fields": (
                "PREMIUM_MENU_LUNCH_default_choice",
                "PREMIUM_MENU_DINNER_default_choice",
            )
        }),

        ("Status Flags", {
            "fields": (
                "user_status_active",
                "lunch_status_active",
                "dinner_status_active",
            )
        }),

        ("Permissions", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),

        ("Important Dates", {
            "fields": (
                "date_joined",
                "profile_updated_at",
            )
        }),
    )

    # =========================
    # ADD USER PAGE
    # =========================
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email",
                "name",
                "password1",
                "password2",
                "subscription_choice",
                "meal_balance",
                "is_active",
                "is_staff",
                "is_superuser",
            ),
        }),
    )

    readonly_fields = ("date_joined", "profile_updated_at")

admin.site.register(LunchRecord)
admin.site.register(DinnerRecord)