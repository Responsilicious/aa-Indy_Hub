"""Tests for the industry job slots overview feature."""
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.urls import reverse

from allianceauth.authentication.models import CharacterOwnership
from allianceauth.eveonline.models import EveCharacter

from indy_hub.models import IndustryJob
from indy_hub.services.esi_client import ESIClientError
from indy_hub.views.industry import industry_job_slots


class IndustryJobSlotsTestCase(TestCase):
    """Test cases for the industry job slots view."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.factory = RequestFactory()

    def setUp(self):
        """Set up test fixtures."""
        self.user = User.objects.create_user(
            username="testuser", password="testpass"
        )
        self.character = EveCharacter.objects.create(
            character_id=123456,
            character_name="Test Character",
            corporation_id=98765,
            corporation_name="Test Corp",
            corporation_ticker="TEST",
        )
        self.ownership = CharacterOwnership.objects.create(
            user=self.user,
            character=self.character,
            owner_hash="testhash",
        )

    def test_url_resolves(self):
        """Test that the job slots URL resolves correctly."""
        url = reverse("indy_hub:industry_job_slots")
        self.assertEqual(url, "/indy_hub/job-slots/")

    @patch("indy_hub.views.industry.shared_client")
    def test_view_with_no_characters(self, mock_client):
        """Test view with user that has no characters."""
        user = User.objects.create_user(username="nochar", password="testpass")
        request = self.factory.get(reverse("indy_hub:industry_job_slots"))
        request.user = user

        # Mock the ESI client
        mock_client.fetch_character_skills.return_value = {"skills": []}

        with patch(
            "indy_hub.views.industry.build_nav_context", return_value={}
        ):
            response = industry_job_slots(request)

        self.assertEqual(response.status_code, 200)

    @patch("indy_hub.views.industry.shared_client")
    def test_view_calculates_manufacturing_slots(self, mock_client):
        """Test that manufacturing slots are calculated correctly."""
        # Mock skills response with Mass Production level 5
        mock_client.fetch_character_skills.return_value = {
            "skills": [
                {"skill_id": 3387, "active_skill_level": 5},  # Mass Production
                {"skill_id": 24625, "active_skill_level": 3},  # Advanced Mass Production
            ]
        }

        request = self.factory.get(reverse("indy_hub:industry_job_slots"))
        request.user = self.user

        with patch(
            "indy_hub.views.industry.build_nav_context", return_value={}
        ):
            response = industry_job_slots(request)

        # Should have 1 (base) + 5 (Mass Production) + 3 (Advanced) = 9 slots
        self.assertEqual(response.status_code, 200)
        context = response.context_data
        char_data = context["character_slots_data"][0]
        self.assertEqual(char_data["manufacturing"]["total"], 9)

    @patch("indy_hub.views.industry.shared_client")
    def test_view_calculates_research_slots(self, mock_client):
        """Test that research slots are calculated correctly."""
        # Mock skills response
        mock_client.fetch_character_skills.return_value = {
            "skills": [
                {"skill_id": 3406, "active_skill_level": 5},  # Laboratory Operation
                {"skill_id": 24624, "active_skill_level": 4},  # Advanced Lab Operation
            ]
        }

        request = self.factory.get(reverse("indy_hub:industry_job_slots"))
        request.user = self.user

        with patch(
            "indy_hub.views.industry.build_nav_context", return_value={}
        ):
            response = industry_job_slots(request)

        context = response.context_data
        char_data = context["character_slots_data"][0]
        # Should have 1 (base) + 5 (Lab Op) + 4 (Advanced) = 10 slots
        self.assertEqual(char_data["research"]["total"], 10)

    @patch("indy_hub.views.industry.shared_client")
    def test_view_calculates_reactions_slots(self, mock_client):
        """Test that reactions slots are calculated correctly."""
        # Mock skills response with reactions skills
        mock_client.fetch_character_skills.return_value = {
            "skills": [
                {"skill_id": 45748, "active_skill_level": 5},  # Mass Reactions
                {"skill_id": 45749, "active_skill_level": 2},  # Advanced Mass Reactions
            ]
        }

        request = self.factory.get(reverse("indy_hub:industry_job_slots"))
        request.user = self.user

        with patch(
            "indy_hub.views.industry.build_nav_context", return_value={}
        ):
            response = industry_job_slots(request)

        context = response.context_data
        char_data = context["character_slots_data"][0]
        # Should have 1 (base) + 5 (Mass Reactions) + 2 (Advanced) = 8 slots
        self.assertEqual(char_data["reactions"]["total"], 8)

    @patch("indy_hub.views.industry.shared_client")
    def test_view_with_no_reactions_skill(self, mock_client):
        """Test that reactions slots are 0 when Mass Reactions is not trained."""
        # Mock skills response without reactions skills
        mock_client.fetch_character_skills.return_value = {
            "skills": [
                {"skill_id": 3387, "active_skill_level": 5},  # Mass Production
            ]
        }

        request = self.factory.get(reverse("indy_hub:industry_job_slots"))
        request.user = self.user

        with patch(
            "indy_hub.views.industry.build_nav_context", return_value={}
        ):
            response = industry_job_slots(request)

        context = response.context_data
        char_data = context["character_slots_data"][0]
        # Should have 0 slots if Mass Reactions not trained
        self.assertEqual(char_data["reactions"]["total"], 0)

    @patch("indy_hub.views.industry.shared_client")
    def test_view_counts_active_jobs(self, mock_client):
        """Test that active jobs are counted correctly."""
        # Mock skills
        mock_client.fetch_character_skills.return_value = {
            "skills": [
                {"skill_id": 3387, "active_skill_level": 5},  # Mass Production
            ]
        }

        # Create some active manufacturing jobs
        for i in range(3):
            IndustryJob.objects.create(
                owner_user=self.user,
                character_id=self.character.character_id,
                job_id=1000 + i,
                installer_id=self.character.character_id,
                activity_id=1,  # Manufacturing
                blueprint_type_id=1000,
                runs=1,
                status="active",
                duration=3600,
                start_date="2024-01-01T00:00:00Z",
                end_date="2024-01-01T01:00:00Z",
            )

        request = self.factory.get(reverse("indy_hub:industry_job_slots"))
        request.user = self.user

        with patch(
            "indy_hub.views.industry.build_nav_context", return_value={}
        ):
            response = industry_job_slots(request)

        context = response.context_data
        char_data = context["character_slots_data"][0]
        # Should show 3 manufacturing jobs in use
        self.assertEqual(char_data["manufacturing"]["used"], 3)
        # Available should be total - used
        self.assertEqual(
            char_data["manufacturing"]["available"],
            char_data["manufacturing"]["total"] - 3,
        )

    @patch("indy_hub.views.industry.shared_client")
    def test_view_handles_esi_error_gracefully(self, mock_client):
        """Test that ESI errors are handled gracefully."""
        # Mock ESI error
        mock_client.fetch_character_skills.side_effect = ESIClientError(
            "Test ESI error"
        )

        request = self.factory.get(reverse("indy_hub:industry_job_slots"))
        request.user = self.user

        with patch(
            "indy_hub.views.industry.build_nav_context", return_value={}
        ):
            response = industry_job_slots(request)

        # Should still return successfully with base slots
        self.assertEqual(response.status_code, 200)
        context = response.context_data
        char_data = context["character_slots_data"][0]
        # Should have base slots only
        self.assertEqual(char_data["manufacturing"]["total"], 1)
        self.assertEqual(char_data["research"]["total"], 1)
        self.assertEqual(char_data["reactions"]["total"], 0)

    @patch("indy_hub.views.industry.shared_client")
    def test_view_calculates_totals_correctly(self, mock_client):
        """Test that totals across all characters are calculated correctly."""
        # Create a second character
        char2 = EveCharacter.objects.create(
            character_id=654321,
            character_name="Test Character 2",
            corporation_id=98765,
            corporation_name="Test Corp",
            corporation_ticker="TEST",
        )
        CharacterOwnership.objects.create(
            user=self.user,
            character=char2,
            owner_hash="testhash2",
        )

        # Mock skills for both characters
        def mock_fetch_skills(char_id):
            return {
                "skills": [
                    {"skill_id": 3387, "active_skill_level": 5},  # Mass Production
                ]
            }

        mock_client.fetch_character_skills.side_effect = mock_fetch_skills

        request = self.factory.get(reverse("indy_hub:industry_job_slots"))
        request.user = self.user

        with patch(
            "indy_hub.views.industry.build_nav_context", return_value={}
        ):
            response = industry_job_slots(request)

        context = response.context_data
        # Should have 2 characters
        self.assertEqual(context["total_characters"], 2)
        # Each character has 6 manufacturing slots (1 base + 5 skill)
        self.assertEqual(context["total_manufacturing_slots"], 12)

    @patch("indy_hub.views.industry.shared_client")
    def test_skills_caching(self, mock_client):
        """Test that skills are cached and reused."""
        from indy_hub.models import CharacterSkillsCache

        # Mock skills response
        skills_data = {
            "skills": [
                {"skill_id": 3387, "active_skill_level": 5},  # Mass Production
            ]
        }
        mock_client.fetch_character_skills.return_value = skills_data

        request = self.factory.get(reverse("indy_hub:industry_job_slots"))
        request.user = self.user

        with patch("indy_hub.views.industry.build_nav_context", return_value={}):
            # First request - should call ESI
            response = industry_job_slots(request)
            self.assertEqual(mock_client.fetch_character_skills.call_count, 1)

            # Second request - should use cache
            mock_client.fetch_character_skills.reset_mock()
            response = industry_job_slots(request)
            self.assertEqual(mock_client.fetch_character_skills.call_count, 0)

        # Verify cache was created
        cache = CharacterSkillsCache.objects.get(character_id=self.character.character_id)
        self.assertEqual(cache.skills_json, skills_data)

    @patch("indy_hub.views.industry.shared_client")
    def test_corporation_scope_permission(self, mock_client):
        """Test corporation scope requires permission."""
        mock_client.fetch_character_skills.return_value = {"skills": []}

        request = self.factory.get(
            reverse("indy_hub:industry_job_slots") + "?scope=corporation"
        )
        request.user = self.user

        with patch("indy_hub.views.industry.build_nav_context", return_value={}):
            with patch("indy_hub.views.industry.messages") as mock_messages:
                response = industry_job_slots(request, scope="corporation")
                # Should redirect due to missing permission
                self.assertEqual(response.status_code, 302)
                mock_messages.error.assert_called()

    @patch("indy_hub.views.industry.shared_client")
    def test_sorting_by_character_name(self, mock_client):
        """Test sorting by character name."""
        # Create second character
        char2 = EveCharacter.objects.create(
            character_id=654321,
            character_name="Alpha Character",  # Will sort before "Test Character"
            corporation_id=98765,
            corporation_name="Test Corp",
            corporation_ticker="TEST",
        )
        CharacterOwnership.objects.create(
            user=self.user,
            character=char2,
            owner_hash="testhash2",
        )

        mock_client.fetch_character_skills.return_value = {"skills": []}

        # Test ascending sort
        request = self.factory.get(
            reverse("indy_hub:industry_job_slots")
            + "?sort=character_name&order=asc"
        )
        request.user = self.user

        with patch("indy_hub.views.industry.build_nav_context", return_value={}):
            response = industry_job_slots(request)

        context = response.context_data
        # Alpha Character should be first
        self.assertEqual(
            context["character_slots_data"][0]["character_name"],
            "Alpha Character"
        )

    @patch("indy_hub.views.industry.shared_client")
    def test_next_free_slot_calculation(self, mock_client):
        """Test that next free slot time is calculated correctly."""
        from datetime import timedelta

        mock_client.fetch_character_skills.return_value = {"skills": []}

        # Create an active manufacturing job ending in 2 hours
        future_date = timezone.now() + timedelta(hours=2, minutes=15)
        IndustryJob.objects.create(
            owner_user=self.user,
            character_id=self.character.character_id,
            job_id=2000,
            installer_id=self.character.character_id,
            activity_id=1,  # Manufacturing
            blueprint_type_id=1000,
            runs=1,
            status="active",
            duration=3600,
            start_date=timezone.now(),
            end_date=future_date,
        )

        request = self.factory.get(reverse("indy_hub:industry_job_slots"))
        request.user = self.user

        with patch("indy_hub.views.industry.build_nav_context", return_value={}):
            response = industry_job_slots(request)

        context = response.context_data
        char_data = context["character_slots_data"][0]
        
        # Should have manufacturing slot used
        self.assertEqual(char_data["manufacturing"]["used"], 1)
        
        # Should have next_free time
        self.assertIsNotNone(char_data["manufacturing"]["next_free"])
        # Should be in format like "2h 15m"
        self.assertIn("h", char_data["manufacturing"]["next_free"])

    @patch("indy_hub.views.industry.shared_client")
    def test_cache_expiry(self, mock_client):
        """Test that expired cache is refreshed."""
        from indy_hub.models import CharacterSkillsCache
        from datetime import timedelta

        # Create expired cache (4 hours old)
        old_skills = {"skills": [{"skill_id": 3387, "active_skill_level": 1}]}
        cache = CharacterSkillsCache.objects.create(
            character_id=self.character.character_id,
            skills_json=old_skills,
            cached_at=timezone.now() - timedelta(hours=4),
        )

        # Mock fresh skills response
        new_skills = {
            "skills": [
                {"skill_id": 3387, "active_skill_level": 5},  # Updated level
            ]
        }
        mock_client.fetch_character_skills.return_value = new_skills

        request = self.factory.get(reverse("indy_hub:industry_job_slots"))
        request.user = self.user

        with patch("indy_hub.views.industry.build_nav_context", return_value={}):
            response = industry_job_slots(request)

        # Should have called ESI to refresh expired cache
        mock_client.fetch_character_skills.assert_called_once()

        # Cache should be updated
        cache.refresh_from_db()
        self.assertEqual(cache.skills_json, new_skills)
