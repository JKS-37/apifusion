import json

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.http import require_POST

from .forms import TeamRegistrationForm
from .models import API_POOL, TeamProfile


class RegisterView(View):
    template_name = "teams/register.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("wheel")
        return render(request, self.template_name, {"form": TeamRegistrationForm()})

    def post(self, request):
        form = TeamRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("wheel")
        return render(request, self.template_name, {"form": form})


class TeamLoginView(LoginView):
    template_name = "teams/login.html"
    redirect_authenticated_user = True


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def wheel_view(request):
    profile, _ = TeamProfile.objects.get_or_create(user=request.user)
    context = {
        "profile": profile,
        "api_pool_json": json.dumps(API_POOL),
        "assigned_json": json.dumps(profile.assigned_apis),
    }
    return render(request, "teams/wheel.html", context)


@login_required
@require_POST
def spin_view(request):
    """
    AJAX endpoint hit by the JS wheel. Server is authoritative:
    it picks the random API, persists it, and returns the result.
    The frontend only uses the returned value to decide where the
    wheel should visually land.
    """
    profile, _ = TeamProfile.objects.get_or_create(user=request.user)

    if profile.is_locked or profile.spin_count >= 2:
        return JsonResponse(
            {"success": False, "error": "Your team is already locked. No more spins allowed."},
            status=400,
        )

    chosen_api, error = profile.spin()
    if error:
        return JsonResponse({"success": False, "error": error}, status=400)

    return JsonResponse({
        "success": True,
        "chosen_api": chosen_api,
        "spin_count": profile.spin_count,
        "is_locked": profile.is_locked,
        "api_1": profile.api_1,
        "api_2": profile.api_2,
        "wheel_index": API_POOL.index(chosen_api),
    })
