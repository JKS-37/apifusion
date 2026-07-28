import random

from django.conf import settings
from django.db import models

# The fixed pool of 16 public APIs used on the wheel.
API_POOL = [
    "Spotify API",
    "TMDB (Movies)",
    "PokéAPI",
    "YouTube API",
    "OpenWeatherMap",
    "OpenStreetMap",
    "NASA API",
    "REST Countries",
    "CoinGecko (Crypto)",
    "Open Food Facts",
    "NewsAPI",
    "ExchangeRate API",
    "Open Trivia DB",
    "Unsplash (Images)",
    "Advice Slip API",
    "GitHub API",
]


class TeamProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="team_profile",
    )
    leader_contact = models.CharField(
        max_length=150,
        help_text="Team leader's email or phone number.",
    )
    spin_count = models.IntegerField(default=0)
    api_1 = models.CharField(max_length=100, null=True, blank=True)
    api_2 = models.CharField(max_length=100, null=True, blank=True)
    is_locked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Team Profile"
        verbose_name_plural = "Team Profiles"

    def __str__(self):
        return self.user.username

    @property
    def team_name(self):
        return self.user.username

    @property
    def assigned_apis(self):
        return [api for api in (self.api_1, self.api_2) if api]

    def already_assigned(self):
        """APIs this team already has, so the wheel never repeats one."""
        return set(self.assigned_apis)

    def pick_random_api(self):
        """
        Choose a random API from the pool that hasn't already been
        assigned to this team. Returns None if the pool is exhausted
        (should not happen with 16 APIs and only 2 spins/team).
        """
        available = [api for api in API_POOL if api not in self.already_assigned()]
        if not available:
            return None
        return random.choice(available)

    def spin(self):
        """
        Server-side authoritative spin logic. Returns the tuple
        (api_name, error) - error is None on success, or a string
        explaining why the spin was rejected.
        """
        if self.is_locked or self.spin_count >= 2:
            return None, "Your team is already locked. No more spins allowed."

        chosen_api = self.pick_random_api()
        if chosen_api is None:
            return None, "No APIs left to assign."

        if self.spin_count == 0:
            self.api_1 = chosen_api
        else:
            self.api_2 = chosen_api

        self.spin_count += 1
        if self.spin_count >= 2:
            self.is_locked = True

        self.save()
        return chosen_api, None
