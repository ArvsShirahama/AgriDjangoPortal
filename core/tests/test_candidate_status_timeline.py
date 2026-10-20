import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from core.models import Candidate, CandidateStatusHistory, AgricultureProgram, ActivityLog


@pytest.fixture
def program(db):
    return AgricultureProgram.objects.create(
        title="AgroStudies Israel Internship",
        description="Agricultural training program",
        country="Israel",
        location="Southern Israel",
        start_date=timezone.now().date() + timedelta(days=30),
        capacity=20
    )


@pytest.fixture
def applicant_user(db):
    user = User.objects.create_user(
        username="applicant_test",
        email="applicant@example.com",
        password="password123",
        first_name="Juan",
        last_name="Dela Cruz"
    )
    return user


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        username="other_user",
        email="other@example.com",
        password="password123"
    )


@pytest.fixture
def staff_user(db):
    return User.objects.create_user(
        username="staff_admin",
        email="staff@example.com",
        password="password123",
        is_staff=True
    )


@pytest.mark.django_db
class TestCandidateStatusTimeline:

    def test_initial_creation_records_history(self, applicant_user, program):
        """Candidate creation should record initial status with from_status=None."""
        CandidateStatusHistory.objects.all().delete()
        candidate = Candidate.objects.create(
            created_by=applicant_user,
            program=program,
            first_name="Juan",
            last_name="Dela Cruz",
            status=Candidate.DRAFT
        )

        history = CandidateStatusHistory.objects.filter(candidate=candidate)
        assert history.count() == 1
        entry = history.first()
        assert entry.status == Candidate.DRAFT
        assert entry.from_status is None
        assert entry.timestamp is not None

    def test_real_status_transition_records_new_history(self, applicant_user, program):
        """Actual status change should record a new transition event."""
        CandidateStatusHistory.objects.all().delete()
        candidate = Candidate.objects.create(
            created_by=applicant_user,
            program=program,
            first_name="Juan",
            last_name="Dela Cruz",
            status=Candidate.DRAFT
        )
        assert CandidateStatusHistory.objects.filter(candidate=candidate).count() == 1

        # Transition Draft -> Missing_Docs
        candidate.status = Candidate.MISSING_DOCS
        candidate.missing_documents_note = "Missing: Passport Scan, TOR"
        candidate.document_deadline = timezone.now() + timedelta(days=7)
        candidate.save()

        history = CandidateStatusHistory.objects.filter(candidate=candidate).order_by('timestamp', 'id')
        assert history.count() == 2
        transition = history.last()
        assert transition.status == Candidate.MISSING_DOCS
        assert transition.from_status == Candidate.DRAFT
        assert "Missing: Passport Scan" in transition.missing_documents_note
        assert transition.document_deadline is not None

        # Transition Missing_Docs -> Validated
        candidate.status = Candidate.VALIDATED
        candidate.save()

        history = CandidateStatusHistory.objects.filter(candidate=candidate).order_by('timestamp', 'id')
        assert history.count() == 3
        latest = history.last()
        assert latest.status == Candidate.VALIDATED
        assert latest.from_status == Candidate.MISSING_DOCS

    def test_unchanged_save_does_not_create_duplicate_history(self, applicant_user, program):
        """Saving candidate without changing status must not create duplicate history events."""
        CandidateStatusHistory.objects.all().delete()
        candidate = Candidate.objects.create(
            created_by=applicant_user,
            program=program,
            first_name="Juan",
            last_name="Dela Cruz",
            status=Candidate.DRAFT
        )
        assert CandidateStatusHistory.objects.filter(candidate=candidate).count() == 1

        # Re-save with updated phone, address, etc.
        candidate.phone_number = "09123456789"
        candidate.address = "123 Farming Lane"
        candidate.save()

        candidate.middle_initial = "M"
        candidate.save()

        # Count should strictly remain 1
        history = CandidateStatusHistory.objects.filter(candidate=candidate)
        assert history.count() == 1

    def test_get_request_does_not_mutate_status_or_create_history(self, client, applicant_user, program):
        """Rendering applicant edit page on GET must not change candidate status or add history."""
        candidate = Candidate.objects.create(
            created_by=applicant_user,
            program=program,
            first_name="Juan",
            last_name="Dela Cruz",
            status=Candidate.DRAFT
        )
        initial_history_count = CandidateStatusHistory.objects.filter(candidate=candidate).count()

        client.force_login(applicant_user)
        url = reverse('edit_candidate', kwargs={'candidate_id': candidate.id})

        # Multiple GET requests
        response1 = client.get(url)
        assert response1.status_code == 200
        assert 'Application Status Timeline' in response1.content.decode('utf-8')

        response2 = client.get(url)
        assert response2.status_code == 200

        # Candidate status in database must remain Draft
        candidate.refresh_from_db()
        assert candidate.status == Candidate.DRAFT

        # No new history rows added by GET requests
        current_history_count = CandidateStatusHistory.objects.filter(candidate=candidate).count()
        assert current_history_count == initial_history_count

    def test_access_control_ownership(self, client, applicant_user, other_user, program):
        """Regular users can only view their own application; others are redirected."""
        candidate = Candidate.objects.create(
            created_by=applicant_user,
            program=program,
            first_name="Juan",
            last_name="Dela Cruz",
            status=Candidate.DRAFT
        )

        # Other user tries to access
        client.force_login(other_user)
        url = reverse('edit_candidate', kwargs={'candidate_id': candidate.id})
        response = client.get(url)
        assert response.status_code == 302
        assert response.url == reverse('profile')

        # Owner accesses
        client.force_login(applicant_user)
        owner_response = client.get(url)
        assert owner_response.status_code == 200
        assert 'Application Status Timeline' in owner_response.content.decode('utf-8')

    def test_staff_edit_page_unaffected(self, client, staff_user, applicant_user, program):
        """Staff visiting candidate edit page should be served candidate_form.html without applicant timeline."""
        candidate = Candidate.objects.create(
            created_by=applicant_user,
            program=program,
            first_name="Juan",
            last_name="Dela Cruz",
            status=Candidate.DRAFT
        )

        client.force_login(staff_user)
        url = reverse('edit_candidate', kwargs={'candidate_id': candidate.id})
        response = client.get(url)
        assert response.status_code == 200
        content = response.content.decode('utf-8')
        # Staff sees standard candidate_form.html
        assert 'candidate_form.html' in [t.name for t in response.templates if t.name]
        # Applicant-specific timeline card is not in candidate_form.html
        assert 'Application Status Timeline' not in content

    def test_empty_history_renders_gracefully(self, client, applicant_user, program):
        """A candidate with zero history records should render cleanly with empty-state notice."""
        candidate = Candidate.objects.create(
            created_by=applicant_user,
            program=program,
            first_name="Maria",
            last_name="Santos",
            status=Candidate.VALIDATED
        )
        # Manually clear history to simulate legacy candidate
        CandidateStatusHistory.objects.filter(candidate=candidate).delete()
        assert CandidateStatusHistory.objects.filter(candidate=candidate).count() == 0

        client.force_login(applicant_user)
        url = reverse('edit_candidate', kwargs={'candidate_id': candidate.id})
        response = client.get(url)
        assert response.status_code == 200
        content = response.content.decode('utf-8')
        assert 'No historical status transitions recorded yet' in content
        assert 'Validated - Ready for Farm Assignment' in content

    def test_milestones_and_missing_document_details(self, client, applicant_user, program):
        """Timeline milestone track displays active/completed state and missing document notes."""
        candidate = Candidate.objects.create(
            created_by=applicant_user,
            program=program,
            first_name="Carlos",
            last_name="Reyes",
            status=Candidate.MISSING_DOCS,
            missing_documents_note="Missing: Diploma, Good Moral Character Certificate",
            document_deadline=timezone.now() + timedelta(days=5)
        )

        client.force_login(applicant_user)
        url = reverse('edit_candidate', kwargs={'candidate_id': candidate.id})
        response = client.get(url)
        assert response.status_code == 200
        content = response.content.decode('utf-8')

        # Milestones displayed with reference photo labels
        assert 'DRAFT' in content
        assert 'MISSING DOCUMENTS' in content
        assert 'VALIDATED' in content
        assert 'APPROVED' in content

        # Check document note and deadline are present
        assert 'Missing: Diploma, Good Moral Character Certificate' in content
        assert 'Upload Deadline:' in content

        # Check privacy: staff username must not be exposed to applicant
        assert 'staff_admin' not in content

    def test_rejected_status_shows_rejected_node(self, client, applicant_user, program):
        """When rejected, a Rejected milestone node is added to the timeline."""
        candidate = Candidate.objects.create(
            created_by=applicant_user,
            program=program,
            first_name="Ana",
            last_name="Cruz",
            status=Candidate.DRAFT
        )
        candidate.status = Candidate.REJECTED
        candidate.save()

        client.force_login(applicant_user)
        url = reverse('edit_candidate', kwargs={'candidate_id': candidate.id})
        response = client.get(url)
        assert response.status_code == 200
        content = response.content.decode('utf-8')
        assert 'REJECTED' in content

    def test_historical_backfill_from_activity_log(self, applicant_user, program):
        """Historical backfill migration correctly reconstructs verified transitions from ActivityLog snapshots."""
        import importlib
        from django.apps import apps
        migration_module = importlib.import_module('core.migrations.0044_backfill_candidate_status_history')
        backfill_candidate_status_history = migration_module.backfill_candidate_status_history

        candidate = Candidate.objects.create(
            created_by=applicant_user,
            program=program,
            first_name="Historical",
            last_name="Test",
            status=Candidate.APPROVED
        )
        # Clear any auto-created history and auto-created logs for this candidate to test migration reconstruction in isolation
        CandidateStatusHistory.objects.filter(candidate=candidate).delete()
        ActivityLog.objects.filter(model_name__icontains='Candidate', object_id=str(candidate.id)).delete()

        # Simulate ActivityLog CREATE (Draft)
        t1 = timezone.now() - timedelta(days=10)
        ActivityLog.objects.create(
            action_type='CREATE',
            model_name='core.Candidate',
            object_id=str(candidate.id),
            before_data=None,
            after_data={'status': 'Draft'},
            timestamp=t1
        )

        # Simulate ActivityLog UPDATE (Draft -> Validated)
        t2 = timezone.now() - timedelta(days=5)
        ActivityLog.objects.create(
            action_type='UPDATE',
            model_name='core.Candidate',
            object_id=str(candidate.id),
            before_data={'status': 'Draft'},
            after_data={'status': 'Validated'},
            timestamp=t2
        )

        # Simulate ActivityLog UPDATE with NO status change (phone number edit)
        t3 = timezone.now() - timedelta(days=3)
        ActivityLog.objects.create(
            action_type='UPDATE',
            model_name='core.Candidate',
            object_id=str(candidate.id),
            before_data={'status': 'Validated', 'phone_number': '111'},
            after_data={'status': 'Validated', 'phone_number': '222'},
            timestamp=t3
        )

        # Simulate ActivityLog UPDATE (Validated -> Approved)
        t4 = timezone.now() - timedelta(days=1)
        ActivityLog.objects.create(
            action_type='UPDATE',
            model_name='core.Candidate',
            object_id=str(candidate.id),
            before_data={'status': 'Validated'},
            after_data={'status': 'Approved'},
            timestamp=t4
        )

        # Run backfill
        backfill_candidate_status_history(apps, None)

        reconstructed = CandidateStatusHistory.objects.filter(candidate=candidate).order_by('timestamp', 'id')
        assert reconstructed.count() == 3
        assert reconstructed[0].status == Candidate.DRAFT
        assert reconstructed[0].from_status is None
        assert reconstructed[1].status == Candidate.VALIDATED
        assert reconstructed[1].from_status == Candidate.DRAFT
        assert reconstructed[2].status == Candidate.APPROVED
        assert reconstructed[2].from_status == Candidate.VALIDATED

