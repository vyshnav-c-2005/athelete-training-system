"""
Test suite: Coach athlete log views
Run with: py manage.py test users.tests.test_coach_log_views --verbosity=2
"""
import datetime
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from users.models import UserProfile
from workouts.models import TrainingSession, ThrowerSession, RunnerSession, JumperSession
from meals.models import NutritionLog, FoodItem, NutritionItem


# ────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────

def make_coach(username="coach1"):
    user = User.objects.create_user(username=username, password="pass123")
    profile = user.userprofile
    profile.role = "Coach"
    profile.save()
    return user, profile


def make_athlete(username="athlete1", coach_profile=None):
    user = User.objects.create_user(username=username, password="pass123")
    profile = user.userprofile
    profile.role = "Athlete"
    if coach_profile:
        profile.coach = coach_profile
    profile.save()
    return user, profile


def make_thrower_session(athlete_user, best_throw_m, date=None, weight_kg=7.26, attempts=3):
    date = date or datetime.date.today()
    session = TrainingSession.objects.create(
        user=athlete_user,
        date=date,
        discipline="shot_put",
        session_type="training",
        athlete_type="thrower",
    )
    ThrowerSession.objects.create(
        session=session,
        implement_weight_kg=weight_kg,
        attempts=attempts,
        best_throw_m=best_throw_m,
    )
    return session


def make_runner_session(athlete_user, distance_m, time_seconds, date=None):
    date = date or datetime.date.today()
    session = TrainingSession.objects.create(
        user=athlete_user,
        date=date,
        discipline="100m",
        session_type="training",
        athlete_type="runner",
    )
    RunnerSession.objects.create(
        session=session,
        distance_m=distance_m,
        time_seconds=time_seconds,
        repetitions=1,
    )
    return session


def make_jumper_session(athlete_user, best_jump_m, date=None):
    date = date or datetime.date.today()
    session = TrainingSession.objects.create(
        user=athlete_user,
        date=date,
        discipline="long_jump",
        session_type="training",
        athlete_type="jumper",
    )
    from workouts.models import JumperSession
    JumperSession.objects.create(
        session=session,
        attempts=3,
        best_jump_m=best_jump_m,
    )
    return session


def make_nutrition_log(athlete_user, meal_type="lunch", date=None):
    date = date or datetime.date.today()
    return NutritionLog.objects.create(
        user=athlete_user,
        date=date,
        day_type="training",
        meal_type=meal_type,
        timing="general",
        carbohydrates_g=50.0,
        protein_g=30.0,
        fats_g=10.0,
        hydration_liters=2.0,
    )


# ────────────────────────────────────────────────────────────────
# Test class
# ────────────────────────────────────────────────────────────────

class CoachLogViewTests(TestCase):

    def setUp(self):
        self.client = Client()

        # Coach
        self.coach_user, self.coach_profile = make_coach("coach1")

        # Athlete assigned to the coach
        self.athlete_user, self.athlete_profile = make_athlete(
            "athlete1", coach_profile=self.coach_profile
        )

        # Unassigned athlete (for permission tests)
        self.other_user, self.other_profile = make_athlete("other1", coach_profile=None)

        # Workouts URL for the athlete
        self.workouts_url = reverse(
            "coach_athlete_workouts", kwargs={"pk": self.athlete_profile.pk}
        )
        # Nutrition URL for the athlete
        self.nutrition_url = reverse(
            "coach_athlete_nutrition", kwargs={"pk": self.athlete_profile.pk}
        )

    # ── Test 1: Thrower-only athlete ──────────────────────────────

    def test_thrower_section_visible_runner_absent(self):
        """Thrower detail section is rendered; runner section is absent."""
        make_thrower_session(self.athlete_user, best_throw_m=18.50)

        self.client.login(username="coach1", password="pass123")
        response = self.client.get(self.workouts_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Thrower Details")
        self.assertContains(response, "18.5")           # best throw value
        self.assertNotContains(response, "Runner Details")

    # ── Test 2: Runner-only athlete ───────────────────────────────

    def test_runner_section_and_pace_displayed(self):
        """Runner section is visible and pace is calculated correctly."""
        # 1000 m in 300 s → pace = 5:00 min/km
        make_runner_session(self.athlete_user, distance_m=1000, time_seconds=300)

        self.client.login(username="coach1", password="pass123")
        response = self.client.get(self.workouts_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Runner Details")
        self.assertContains(response, "5:00")           # pace in mm:ss
        self.assertNotContains(response, "Thrower Details")

    # ── Test 3: Nutrition — multiple foods, correct totals ────────

    def test_nutrition_multiple_foods_and_totals(self):
        """Food rows are present and computed totals are correct."""
        log = make_nutrition_log(self.athlete_user)

        food = FoodItem.objects.create(
            name="Oat Flakes",
            carbs_per_100g=66.0,
            protein_per_100g=17.0,
            fats_per_100g=7.0,
        )
        # 100 g of Oat Flakes
        NutritionItem.objects.create(
            nutrition_log=log,
            food_item=food,
            quantity_g=100,
            carbohydrates_g=66.0,
            protein_g=17.0,
            fats_g=7.0,
        )
        # 50 g more
        NutritionItem.objects.create(
            nutrition_log=log,
            food_item=food,
            quantity_g=50,
            carbohydrates_g=33.0,
            protein_g=8.5,
            fats_g=3.5,
        )

        self.client.login(username="coach1", password="pass123")
        response = self.client.get(self.nutrition_url)

        self.assertEqual(response.status_code, 200)
        # Both food rows should appear
        self.assertContains(response, "Oat Flakes")
        content = response.content.decode()
        self.assertEqual(content.count("Oat Flakes"), 2)

        # Totals: carbs 99, protein 25.5, fats 10.5
        self.assertContains(response, "99.0")
        self.assertContains(response, "25.5")
        self.assertContains(response, "10.5")

    # ── Test 4: Nutrition — zero foods shows empty message ────────

    def test_nutrition_zero_foods_empty_message(self):
        """When a log has no food items, an 'No foods' message is shown."""
        make_nutrition_log(self.athlete_user)

        self.client.login(username="coach1", password="pass123")
        response = self.client.get(self.nutrition_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No foods logged")

    # ── Test 5: Pagination — 25 sessions ─────────────────────────

    def test_workout_pagination_25_sessions(self):
        """25 sessions → page 1 has 20 items, page 2 has 5 items."""
        base = datetime.date(2025, 1, 1)
        for i in range(25):
            make_thrower_session(
                self.athlete_user,
                best_throw_m=10.0 + i,
                date=base + datetime.timedelta(days=i),
            )

        self.client.login(username="coach1", password="pass123")

        # Page 1
        r1 = self.client.get(self.workouts_url + "?page=1")
        self.assertEqual(r1.status_code, 200)
        self.assertEqual(len(r1.context["sessions_page"].object_list), 20)

        # Page 2
        r2 = self.client.get(self.workouts_url + "?page=2")
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(len(r2.context["sessions_page"].object_list), 5)

    # ── Test 6: Permission enforcement ───────────────────────────

    def test_athlete_cannot_access_coach_workout_view(self):
        """An athlete user must NOT be able to access the coach workouts page."""
        self.client.login(username="athlete1", password="pass123")
        response = self.client.get(self.workouts_url)

        # Should redirect (302) not show the page
        self.assertNotEqual(response.status_code, 200)
        self.assertIn(response.status_code, [302, 403])

    # ── Test 7: Personal Best flagged ─────────────────────────────

    def test_pb_session_flagged(self):
        """The session with the highest best_throw_m should show the PB badge."""
        base = datetime.date(2025, 3, 1)
        make_thrower_session(self.athlete_user, best_throw_m=15.0, date=base)
        make_thrower_session(self.athlete_user, best_throw_m=20.5, date=base + datetime.timedelta(days=1))
        make_thrower_session(self.athlete_user, best_throw_m=18.0, date=base + datetime.timedelta(days=2))

        self.client.login(username="coach1", password="pass123")
        response = self.client.get(self.workouts_url)

        self.assertEqual(response.status_code, 200)
        # PB badge should appear exactly once
        content = response.content.decode()
        self.assertIn("Personal Best", content)
        self.assertIn("20.5", content)
