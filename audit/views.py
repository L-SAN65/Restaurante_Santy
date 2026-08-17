from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import AuditLog


@login_required
def audit_trail(request):
    entries = AuditLog.objects.select_related("user")[:200]
    return render(request, "audit/trail.html", {"entries": entries})