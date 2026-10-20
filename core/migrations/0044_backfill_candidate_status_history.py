# Data migration to backfill CandidateStatusHistory from verified ActivityLog snapshots
from django.db import migrations
from django.utils.dateparse import parse_datetime


def backfill_candidate_status_history(apps, schema_editor):
    Candidate = apps.get_model('core', 'Candidate')
    ActivityLog = apps.get_model('core', 'ActivityLog')
    CandidateStatusHistory = apps.get_model('core', 'CandidateStatusHistory')

    valid_statuses = {'Draft', 'Missing_Docs', 'Validated', 'Approved', 'Rejected'}

    # Process each candidate
    for candidate in Candidate.objects.all():
        logs = ActivityLog.objects.filter(
            model_name__icontains='Candidate',
            object_id=str(candidate.id)
        ).order_by('timestamp', 'id')

        last_status = None
        for log in logs:
            action = log.action_type
            before = log.before_data or {}
            after = log.after_data or {}

            # Handle CREATE action: initial status
            if action == 'CREATE':
                st = after.get('status')
                if st and st in valid_statuses:
                    deadline_raw = after.get('document_deadline')
                    deadline = parse_datetime(deadline_raw) if isinstance(deadline_raw, str) else deadline_raw
                    CandidateStatusHistory.objects.create(
                        candidate=candidate,
                        status=st,
                        from_status=None,
                        timestamp=log.timestamp,
                        missing_documents_note=after.get('missing_documents_note') or '',
                        document_deadline=deadline,
                        notes='Initial application creation (verified from audit log)'
                    )
                    last_status = st

            # Handle UPDATE action: status transition
            elif action == 'UPDATE':
                b_st = before.get('status')
                a_st = after.get('status')
                # Only record when status genuinely changed
                if a_st and a_st in valid_statuses and b_st != a_st:
                    deadline_raw = after.get('document_deadline')
                    deadline = parse_datetime(deadline_raw) if isinstance(deadline_raw, str) else deadline_raw
                    CandidateStatusHistory.objects.create(
                        candidate=candidate,
                        status=a_st,
                        from_status=b_st or last_status,
                        timestamp=log.timestamp,
                        missing_documents_note=after.get('missing_documents_note') or '',
                        document_deadline=deadline,
                        notes='Status update (verified from audit log)'
                    )
                    last_status = a_st


def reverse_backfill(apps, schema_editor):
    CandidateStatusHistory = apps.get_model('core', 'CandidateStatusHistory')
    CandidateStatusHistory.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0043_candidatestatushistory'),
    ]

    operations = [
        migrations.RunPython(backfill_candidate_status_history, reverse_backfill),
    ]
