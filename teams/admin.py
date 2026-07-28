import csv

from django.contrib import admin
from django.http import HttpResponse

from .models import TeamProfile


@admin.action(description="Export selected teams to CSV")
def export_as_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="api_fusion_allocations.csv"'

    writer = csv.writer(response)
    writer.writerow(["Team Name", "Leader Contact", "Spin Count", "API 1", "API 2", "Is Locked", "Created At"])

    for profile in queryset:
        writer.writerow([
            profile.team_name,
            profile.leader_contact,
            profile.spin_count,
            profile.api_1 or "",
            profile.api_2 or "",
            "Yes" if profile.is_locked else "No",
            profile.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        ])

    return response


@admin.register(TeamProfile)
class TeamProfileAdmin(admin.ModelAdmin):
    list_display = (
        "team_name_display",
        "leader_contact",
        "spin_count",
        "api_1",
        "api_2",
        "is_locked",
        "created_at",
    )
    search_fields = ("user__username", "leader_contact")
    list_filter = ("is_locked", "spin_count")
    ordering = ("-created_at",)
    actions = [export_as_csv]
    readonly_fields = ("created_at",)

    @admin.display(description="Team Name", ordering="user__username")
    def team_name_display(self, obj):
        return obj.team_name
