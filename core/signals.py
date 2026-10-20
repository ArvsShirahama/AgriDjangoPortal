import logging
from django.db.models.signals import pre_save, post_save, pre_delete
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from django.forms.models import model_to_dict
from django.apps import apps
from django.db import connection
from .models import Profile, ActivityLog, Registration, Candidate, CandidateStatusHistory
from .middleware import get_request_user, get_request_ip, get_request_session_key
from .utils.file_tracker import register_model_files

logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    Create a user profile whenever a new User is created
    """
    if created:
        Profile.objects.create(user=instance)

# -------- Generic CRUD auditing ---------
_pre_save_cache = {}
_activitylog_table_exists = None


def _activitylog_ready():
    global _activitylog_table_exists
    if _activitylog_table_exists is None:
        try:
            tables = set(connection.introspection.table_names())
            _activitylog_table_exists = ActivityLog._meta.db_table in tables
        except Exception:
            _activitylog_table_exists = False
    return _activitylog_table_exists

def _model_label(instance):
    return f"{instance._meta.app_label}.{instance.__class__.__name__}"

def _serialize_instance(instance):
    """Serialize model instance to a plain dict of editable concrete field values.
    ForeignKey fields will be stored as their raw id value.
    """
    data = {}
    for field in instance._meta.get_fields():
        if not getattr(field, 'concrete', False):
            continue
        if getattr(field, 'many_to_many', False) or getattr(field, 'one_to_many', False):
            continue  # skip relations that need separate queries
        if hasattr(field, 'attname'):
            name = field.attname.replace('_id', '') if field.is_relation else field.attname
        else:
            name = field.name
        try:
            val = getattr(instance, field.attname if hasattr(field, 'attname') else field.name)
        except Exception:
            continue
        # For bytes/files use string representation
        if hasattr(val, 'name'):
            val = val.name
        data[name] = val
    return data

@receiver(pre_save)
def log_pre_save(sender, instance, **kwargs):
    # Only track project models, skip Django internal apps
    if not hasattr(instance, '_meta'):
        return
    label = _model_label(instance)
    # Avoid logging ActivityLog itself to prevent recursion
    if label == 'core.ActivityLog':
        return
    # Only audit our app models
    if instance._meta.app_label != 'core':
        return
    if instance.pk:
        # Existing -> capture before snapshot
        try:
            existing = sender.objects.get(pk=instance.pk)
            _pre_save_cache[(label, instance.pk)] = _serialize_instance(existing)
        except sender.DoesNotExist:
            _pre_save_cache[(label, instance.pk)] = None
    else:
        _pre_save_cache[(label, None)] = None

@receiver(post_save)
def log_post_save(sender, instance, created, **kwargs):
    if not hasattr(instance, '_meta'):
        return
    label = _model_label(instance)
    if label == 'core.ActivityLog':
        return
    if instance._meta.app_label != 'core':
        return
    after = _serialize_instance(instance)
    key = (label, instance.pk if not created else None)
    before = _pre_save_cache.pop(key, None)
    action = ActivityLog.ACTION_CREATE if created else ActivityLog.ACTION_UPDATE
    if not _activitylog_ready():
        return
    user = get_request_user()
    if user and not user.is_authenticated:
        user = None
    try:
        ActivityLog.objects.create(
            user=user,
            action_type=action,
            model_name=label,
            object_id=str(instance.pk),
            before_data=before,
            after_data=after,
            ip_address=get_request_ip(),
            session_key=get_request_session_key(),
        )
    except Exception:
        logger.exception('Failed to write ActivityLog for %s', label)

@receiver(pre_delete)
def log_pre_delete(sender, instance, **kwargs):
    if not hasattr(instance, '_meta'):
        return
    label = _model_label(instance)
    if label == 'core.ActivityLog':
        return
    if instance._meta.app_label != 'core':
        return
    before = _serialize_instance(instance)
    if not _activitylog_ready():
        return
    user = get_request_user()
    if user and not user.is_authenticated:
        user = None
    try:
        ActivityLog.objects.create(
            user=user,
            action_type=ActivityLog.ACTION_DELETE,
            model_name=label,
            object_id=str(instance.pk),
            before_data=before,
            after_data=None,
            ip_address=get_request_ip(),
            session_key=get_request_session_key(),
        )
    except Exception:
        logger.exception('Failed to write ActivityLog (DELETE) for %s', label)

# -------- Auth auditing ---------

@receiver(user_logged_in)
def on_user_logged_in(sender, request, user, **kwargs):
    ActivityLog.objects.create(
        user=user,
        action_type=ActivityLog.ACTION_LOGIN,
        model_name='auth.User',
        object_id=str(user.pk),
        before_data=None,
        after_data={'username': user.username},
        ip_address=get_request_ip(),
        session_key=get_request_session_key(),
    )

@receiver(user_logged_out)
def on_user_logged_out(sender, request, user, **kwargs):
    ActivityLog.objects.create(
        user=user,
        action_type=ActivityLog.ACTION_LOGOUT,
        model_name='auth.User',
        object_id=str(getattr(user, 'pk', '')),
        before_data={'username': getattr(user, 'username', '')},
        after_data=None,
        ip_address=get_request_ip(),
        session_key=get_request_session_key(),
    )

@receiver(user_login_failed)
def on_user_login_failed(sender, credentials, request, **kwargs):
    username = credentials.get('username') if isinstance(credentials, dict) else ''
    ActivityLog.objects.create(
        user=None,
        action_type=ActivityLog.ACTION_FAILED_LOGIN,
        model_name='auth.User',
        object_id=None,
        before_data={'username': username},
        after_data=None,
        ip_address=get_request_ip(),
        session_key=get_request_session_key(),
    )

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """
    Save the user profile whenever a User is saved
    """
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        # Create the profile if it doesn't exist
        Profile.objects.create(user=instance)


# -------- File Upload Tracking ---------

@receiver(post_save, sender=Profile)
def track_profile_files(sender, instance, created, **kwargs):
    """
    Automatically register file uploads from Profile model to UploadedFile tracking system.
    Only registers NEW or CHANGED files by comparing file hash.
    """
    if instance.user and instance.pk:
        try:
            from core.models import UploadedFile
            
            document_fields = [
                'profile_image', 'license_scan', 'passport_scan', 'academic_certificate',
                'tor', 'nc2_tesda', 'diploma', 'good_moral', 'nbi_clearance'
            ]
            
            # Quick check: does this profile have ANY files at all?
            has_any_file = False
            for field_name in document_fields:
                current_file = getattr(instance, field_name, None)
                if current_file and hasattr(current_file, 'name') and current_file.name:
                    has_any_file = True
                    break
            
            if not has_any_file:
                return
            
            # Track which files we process to avoid duplicate processing
            for field_name in document_fields:
                current_file = getattr(instance, field_name, None)
                
                # Only process if there's a file
                if current_file and hasattr(current_file, 'name') and current_file.name:
                    try:
                        # Calculate hash of current file
                        # Use its current open state if possible, otherwise open carefully
                        is_opened = hasattr(current_file, 'file') and current_file.file is not None
                        
                        try:
                            if not is_opened:
                                current_file.open('rb')
                            else:
                                current_file.seek(0)
                                
                            current_hash = UploadedFile.calculate_file_hash(current_file)
                            current_file.seek(0) # Always reset pointer after reading
                        finally:
                            if not is_opened:
                                current_file.close()

                        # Get existing record for this field
                        existing_record = UploadedFile.objects.filter(
                            user=instance.user,
                            document_type=field_name,
                            is_active=True
                        ).first()
                        
                        # Check if this file is different from what we have recorded
                        should_register = False
                        
                        if not existing_record:
                            # No existing record - this is a new upload
                            should_register = True
                        elif existing_record.file_hash != current_hash:
                            # Hash changed - user replaced the file
                            should_register = True
                            # Deactivate the old record since it's being replaced
                            existing_record.is_active = False
                            existing_record.save()
                        # else: Same file, same field - don't re-register
                        
                        if should_register:
                            # Register with UploadedFile
                            is_opened = hasattr(current_file, 'file') and current_file.file is not None
                            try:
                                if not is_opened:
                                    current_file.open('rb')
                                else:
                                    current_file.seek(0)
                                    
                                UploadedFile.register_upload(
                                    user=instance.user,
                                    document_type=field_name,
                                    file_obj=current_file,
                                    model_name='Profile',
                                    model_id=instance.pk
                                )
                                current_file.seek(0) # Reset after registration
                            finally:
                                if not is_opened:
                                    current_file.close()
                            
                    except Exception as file_error:
                        logger.warning(f"Error processing file {field_name} for profile {instance.pk}: {str(file_error)}")
                        
        except Exception as e:
            logger.error(f"Error tracking Profile files for user {instance.user.username}: {str(e)}")


@receiver(post_save, sender=Profile)
def sync_profile_documents_to_candidates(sender, instance, created, **kwargs):
    """
    Automatically sync documents from Profile to all associated Candidate records.
    When user updates their profile documents, all their candidate applications get updated.
    """
    if not instance.user or not instance.pk:
        return
    
    try:
        # Find all candidates created by this user
        candidates = Candidate.objects.filter(created_by=instance.user)
        
        if not candidates.exists():
            return
        
        # Document field mapping: Profile field -> Candidate field
        document_mapping = {
            'profile_image': 'profile_image',
            'license_scan': 'license_scan',
            'passport_scan': 'passport_scan',
            'academic_certificate': 'academic_certificate',
            'tor': 'tor',
            'nc2_tesda': 'nc2_tesda',
            'diploma': 'diploma',
            'good_moral': 'good_moral',
            'nbi_clearance': 'nbi_clearance',
        }
        
        # Update each candidate
        updated_count = 0
        for candidate in candidates:
            updated = False
            
            for profile_field, candidate_field in document_mapping.items():
                profile_file = getattr(instance, profile_field, None)
                current_candidate_file = getattr(candidate, candidate_field, None)
                
                # Sync the file (copy reference from profile to candidate)
                if profile_file and hasattr(profile_file, 'name') and profile_file.name:
                    # Profile has a file - copy it to candidate
                    if not current_candidate_file or current_candidate_file.name != profile_file.name:
                        setattr(candidate, candidate_field, profile_file)
                        updated = True
                        logger.info(f"Synced {profile_field} from profile to candidate {candidate.pk}")
                elif not profile_file and current_candidate_file:
                    # Profile file was removed - remove from candidate too
                    setattr(candidate, candidate_field, None)
                    updated = True
                    logger.info(f"Removed {candidate_field} from candidate {candidate.pk} (removed from profile)")
            
            if updated:
                candidate.save()
                updated_count += 1
        
        if updated_count > 0:
            logger.info(f"Synced documents from profile {instance.pk} to {updated_count} candidate(s)")
    
    except Exception as e:
        logger.error(f"Error syncing Profile documents to Candidates for user {instance.user.username}: {str(e)}")


@receiver(post_save, sender=Registration)
def track_registration_files(sender, instance, created, **kwargs):
    """
    Automatically register file uploads from Registration model to UploadedFile tracking system.
    """
    if instance.user and instance.pk:
        try:
            register_model_files(instance, instance.user, 'Registration')
        except Exception as e:
            logger.error(f"Error tracking Registration files for user {instance.user.username}: {str(e)}")


@receiver(post_save, sender=Candidate)
def track_candidate_files(sender, instance, created, **kwargs):
    """
    Automatically register file uploads from Candidate model to UploadedFile tracking system.
    Uses created_by (staff member) as the tracking user.
    """
    if instance.created_by and instance.pk:
        try:
            register_model_files(instance, instance.created_by, 'Candidate')
        except Exception as e:
            logger.error(f"Error tracking Candidate files for candidate {instance.pk}: {str(e)}")


@receiver(pre_save, sender=Candidate)
def track_candidate_status_pre_save(sender, instance, **kwargs):
    """Capture prior status before Candidate is saved to detect genuine transitions."""
    if instance.pk:
        try:
            prior = Candidate.objects.filter(pk=instance.pk).values('status').first()
            instance._prior_status = prior['status'] if prior else None
        except Exception:
            instance._prior_status = None
    else:
        instance._prior_status = None


@receiver(post_save, sender=Candidate)
def record_candidate_status_history(sender, instance, created, **kwargs):
    """
    Record initial status and all real status transitions in CandidateStatusHistory.
    Never creates duplicate entries on unchanged saves.
    """
    try:
        from django.utils import timezone
        if created:
            CandidateStatusHistory.objects.create(
                candidate=instance,
                status=instance.status,
                from_status=None,
                timestamp=getattr(instance, 'created_at', None) or timezone.now(),
                missing_documents_note=instance.missing_documents_note or '',
                document_deadline=instance.document_deadline
            )
        elif hasattr(instance, '_prior_status') and instance._prior_status != instance.status:
            CandidateStatusHistory.objects.create(
                candidate=instance,
                status=instance.status,
                from_status=instance._prior_status,
                timestamp=timezone.now(),
                missing_documents_note=instance.missing_documents_note or '',
                document_deadline=instance.document_deadline
            )
    except Exception as e:
        logger.error(f"Error recording CandidateStatusHistory for candidate {instance.pk}: {str(e)}")
 