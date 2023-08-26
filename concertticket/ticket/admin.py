from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.urls import reverse
from django.utils.html import format_html
from import_export.admin import ImportExportActionModelAdmin

from .forms import TicketAdminForm
from .models import Concert, Ticket, Venue, ConcertCategory


class SoldOutFilter(SimpleListFilter):
    title = "Sold out"
    parameter_name = 'sold_out'

    def lookups(self, request, model_admin):
        return [
            ('yes', "Yes"),
            ('no', 'No'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(tickets_left=0)
        else:
            return queryset.exclude(tickets_left=0)


class ConcertInline(admin.TabularInline):
    model = Concert
    fields = ["name", "starts_at", "price", "tickets_left"]

    readonly_fields = ["name", "starts_at", "price", "tickets_left"]
    can_delete = False
    max_num = 0
    extra = 0
    show_change_link = True


class ConcertAdmin(admin.ModelAdmin):
    list_display = ["name", "venue", "starts_at", "price", "tickets_left", "display_sold_out", "display_price",
                    "display_venue"]
    list_select_related = ["venue"]
    list_filter = ["venue", SoldOutFilter]
    search_fields = ["name", "venue__name", "venue__address"]
    readonly_fields = ["tickets_left"]

    def display_sold_out(self, obj):
        return obj.tickets_left == 0

    display_sold_out.short_description = "Sold out"
    display_sold_out.boolean = True

    def display_price(self, obj):
        return f"{obj.price}"

    display_price.short_description = "Price"
    display_price.admin_order_field = "price"

    def display_venue(self, obj):
        link = reverse("admin:ticket_venue_change", args=[obj.venue.id])
        return format_html('<a href="{}">{}</a>', link, obj.venue)

    display_venue.short_description = "Venue"


class VenueAdmin(admin.ModelAdmin):
    list_display = ["name", "address", "capacity"]
    inlines = [ConcertInline]


@admin.action(description="Activate selected tickets")
def acivate_tickets(modeladmin, request, queryset):
    return queryset.update(is_active=True)


@admin.action(description="Deactivate selected tickets")
def deactivate_tickets(modeladmin, request, queryset):
    queryset.update(is_active=False)


class TicketAdmin(ImportExportActionModelAdmin):
    list_display = [
        "customer_full_name", "concert",
        "payment_method", "paid_at", "is_active",
    ]
    list_select_related = ["concert", "concert__venue"]
    actions = [acivate_tickets, deactivate_tickets]
    form = TicketAdminForm


class ConcertCategoryAdmin(admin.ModelAdmin):
    pass


admin.site.register(Concert, ConcertAdmin)
admin.site.register(Venue, VenueAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(ConcertCategory, ConcertCategoryAdmin)
