from django.db import models, transaction

from django.contrib.auth.models import User

from django.apps import apps

from django.core.serializers.json import DjangoJSONEncoder

from django.utils import timezone

import hashlib

import os





class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    bio = models.TextField(blank=True)

    location = models.CharField(max_length=100, blank=True)

    date_joined = models.DateTimeField(auto_now_add=True)

    email_verified = models.BooleanField(default=False)

    verification_token = models.CharField(max_length=100, blank=True, null=True)

    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    phone_number = models.CharField(max_length=20, blank=True, null=True)

    

    # Extended personal information for syncing with applications

    middle_initial = models.CharField(max_length=5, blank=True, null=True, verbose_name="Middle Initial")

    father_name = models.CharField(max_length=100, blank=True, null=True)

    mother_name = models.CharField(max_length=100, blank=True, null=True)

    date_of_birth = models.DateField(blank=True, null=True)

    country_of_birth = models.CharField(max_length=100, blank=True, null=True)

    nationality = models.CharField(max_length=100, blank=True, null=True)

    religion = models.CharField(max_length=100, blank=True, null=True)

    

    GENDER_CHOICES = [

        ('Male', 'Male'),

        ('Female', 'Female'),

    ]

    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)

    has_international_license = models.BooleanField(default=False)

    license_scan = models.FileField(upload_to='licenses/', blank=True, null=True)

    

    # Extended registration fields

    address = models.TextField(blank=True, null=True, verbose_name="Address")

    passport_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Passport Number")

    passport_issue_date = models.DateField(blank=True, null=True, verbose_name="Passport Issue Date")

    passport_expiry_date = models.DateField(blank=True, null=True, verbose_name="Passport Expiry Date")

    place_of_issue = models.CharField(max_length=100, blank=True, null=True, verbose_name="Place of Issue")

    

    EDUCATION_LEVEL_CHOICES = [

        ('high_school', 'High School'),

        ('bachelor', "Bachelor's Degree"),

        ('master', "Master's Degree"),

        ('phd', 'PhD'),

        ('other', 'Other'),

    ]

    highest_education_level = models.CharField(max_length=20, choices=EDUCATION_LEVEL_CHOICES, blank=True, null=True, verbose_name="Highest Education Level")

    graduation_year = models.PositiveIntegerField(blank=True, null=True, verbose_name="Graduation Year")

    field_of_study = models.CharField(max_length=100, blank=True, null=True, verbose_name="Field of Study")

    

    # Additional candidate-style fields for comprehensive profile

    university = models.CharField(max_length=200, blank=True, null=True, verbose_name="University")

    specialization = models.CharField(max_length=100, blank=True, null=True, verbose_name="Primary Specialization")

    secondary_specialization = models.CharField(max_length=100, blank=True, null=True, verbose_name="Secondary Specialization")

    year_graduated = models.PositiveIntegerField(blank=True, null=True, verbose_name="Year Graduated")

    

    SMOKING_CHOICES = [

        ('Never', 'Never'),

        ('Sometimes', 'Sometimes'),

        ('Often', 'Often'),

    ]

    smokes = models.CharField(max_length=10, choices=SMOKING_CHOICES, default='Never', verbose_name="Smoking Habits")

    

    shoes_size = models.CharField(max_length=10, blank=True, null=True, verbose_name="Shoes Size")

    shirt_size = models.CharField(max_length=10, blank=True, null=True, verbose_name="Shirt Size")

    job_experience = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Job Experience",
        help_text="Describe your relevant work/job experience"
    )

    preferred_country = models.CharField(max_length=100, blank=True, null=True, verbose_name="Preferred Country")

    willing_to_relocate = models.BooleanField(default=True, verbose_name="Willing to Relocate")

    special_requirements = models.TextField(blank=True, null=True, verbose_name="Special Requirements")



    HEALTH_CHOICES = [

        ('Excellent', 'Excellent'),

        ('Fair', 'Fair'),

        ('Poor', 'Poor'),

    ]

    health_condition = models.CharField(max_length=20, choices=HEALTH_CHOICES, blank=True, null=True, verbose_name="Health Condition")

    health_remarks = models.TextField(blank=True, null=True, verbose_name="Health Remarks")

    

    passport_scan = models.FileField(upload_to='passport_scans/', blank=True, null=True, verbose_name="Passport Scan")

    academic_certificate = models.FileField(upload_to='academic_certificates/', blank=True, null=True, verbose_name="Academic Certificate")



    # Additional required documents for registration

    tor = models.FileField(upload_to='documents/tor/', blank=True, null=True, verbose_name="Transcript of Records (TOR)")

    nc2_tesda = models.FileField(upload_to='documents/tesda/', blank=True, null=True, verbose_name="NC2 from TESDA")

    diploma = models.FileField(upload_to='documents/diploma/', blank=True, null=True, verbose_name="Diploma")

    good_moral = models.FileField(upload_to='documents/moral/', blank=True, null=True, verbose_name="Good Moral Character")

    nbi_clearance = models.FileField(upload_to='documents/nbi/', blank=True, null=True, verbose_name="NBI Clearance")

    

    # OAuth 2.0 Social Authentication Fields

    OAUTH_PROVIDER_CHOICES = [

        ('google', 'Google'),

        ('facebook', 'Facebook'),

        ('microsoft', 'Microsoft'),

        ('email', 'Email'),

    ]

    oauth_provider = models.CharField(

        max_length=20,

        choices=OAUTH_PROVIDER_CHOICES,

        blank=True,

        null=True,

        verbose_name="OAuth Provider",

        help_text="The social authentication provider used to create this account"

    )

    oauth_id = models.CharField(

        max_length=255,

        blank=True,

        null=True,

        unique=True,

        verbose_name="OAuth Provider ID",

        help_text="The unique ID from the OAuth provider"

    )

    oauth_picture_url = models.URLField(

        blank=True,

        null=True,

        verbose_name="OAuth Profile Picture URL",

        help_text="Original profile picture URL from OAuth provider"

    )

    

    def __str__(self):

        return f"{self.user.username}'s profile"



    @property

    def age(self):

        if not self.date_of_birth:

            return None

        today = timezone.now().date()

        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))





class AgricultureProgram(models.Model):

    title = models.CharField(max_length=200)

    description = models.TextField()

    start_date = models.DateField()

    country = models.CharField(max_length=100, help_text='Country where the program is located')

    location = models.CharField(max_length=100, help_text='Specific location within the country')

    capacity = models.PositiveIntegerField()

    registration_deadline = models.DateTimeField(blank=True, null=True, 

        help_text='Deadline for program registration. If not set, registration will be open until start date.')

    image = models.ImageField(upload_to='program_images/', blank=True, null=True, help_text='Program/Farm image')

    is_featured = models.BooleanField(default=False, help_text='Display on landing page as featured program')

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    

    GENDER_REQUIREMENT_CHOICES = [

        ('Any', 'Any'),

        ('Male', 'Male Only'),

        ('Female', 'Female Only'),

    ]

    required_gender = models.CharField(max_length=10, choices=GENDER_REQUIREMENT_CHOICES, default='Any')

    requires_license = models.BooleanField(default=False, verbose_name="Requires International Driver's License")

    required_experience_years = models.PositiveIntegerField(

        default=0,

        verbose_name="Required Job Experience (Years)",

        help_text="Minimum years of relevant job experience required. Set to 0 if no experience required."

    )

    

    def __str__(self):

        return self.title

    

    def is_registration_open(self):

        """Check if registration is still open for this program"""

        now = timezone.now()

        

        # If registration deadline is set, use that

        if self.registration_deadline:

            return now <= self.registration_deadline

            

        # If no deadline set, use start date

        return now.date() <= self.start_date

    

    def get_image_url(self):

        """Return image URL or placeholder"""

        if self.image:

            return self.image.url

        

        # Check if placeholder image exists, otherwise use placehold.co

        import os

        from django.conf import settings

        

        placeholders = {

            'Israel': 'israel-farm.jpg',

            'Japan': 'japan-farm.jpg',

            'Australia': 'australia-farm.jpg',

            'New Zealand': 'newzealand-farm.jpg',

        }

        

        placeholder_file = placeholders.get(self.location, 'default-farm.jpg')

        placeholder_path = os.path.join(settings.STATIC_ROOT or 'static', 'images', 'placeholders', placeholder_file)

        

        # If placeholder image exists, use it; otherwise use placehold.co

        if os.path.exists(placeholder_path):

            return f'/static/images/placeholders/{placeholder_file}'

        else:

            # Use placehold.co as fallback with location name

            location_text = self.location.replace(' ', '+')

            return f'https://placehold.co/800x400/228B22/FFFFFF/png?text={location_text}+Farm'

    

    class Meta:

        ordering = ['-is_featured', '-created_at']





class Registration(models.Model):

    PENDING = 'pending'

    APPROVED = 'approved'

    REJECTED = 'rejected'

    STATUS_CHOICES = [

        (PENDING, 'Pending'),

        (APPROVED, 'Approved'),

        (REJECTED, 'Rejected'),

    ]

    

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    program = models.ForeignKey(AgricultureProgram, on_delete=models.CASCADE)

    registration_date = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)

    notes = models.TextField(blank=True)

    processed = models.BooleanField(default=False)  # Flag to indicate if this registration has been processed into a candidate

    

    # Required documents (matching the Candidate model fields)

    tor = models.FileField(upload_to='documents/tor/', blank=True, null=True, verbose_name="Transcript of Records (TOR)")

    nc2_tesda = models.FileField(upload_to='documents/tesda/', blank=True, null=True, verbose_name="NC2 from TESDA")

    diploma = models.FileField(upload_to='documents/diploma/', blank=True, null=True)

    good_moral = models.FileField(upload_to='documents/moral/', blank=True, null=True, verbose_name="Good Moral Character")

    nbi_clearance = models.FileField(upload_to='documents/nbi/', blank=True, null=True, verbose_name="NBI Clearance")

    

    class Meta:

        unique_together = ('user', 'program')

        

    def __str__(self):

        return f"{self.user.username} - {self.program.title}"

    

    def copy_documents_to_candidate(self, candidate):

        """Copy uploaded documents to a candidate profile"""

        if self.tor and not candidate.tor:

            candidate.tor = self.tor

        if self.nc2_tesda and not candidate.nc2_tesda:

            candidate.nc2_tesda = self.nc2_tesda

        if self.diploma and not candidate.diploma:

            candidate.diploma = self.diploma

        if self.good_moral and not candidate.good_moral:

            candidate.good_moral = self.good_moral

        if self.nbi_clearance and not candidate.nbi_clearance:

            candidate.nbi_clearance = self.nbi_clearance

        candidate.save()





class University(models.Model):

    name = models.CharField(max_length=200)

    code = models.CharField(max_length=20, unique=True)

    country = models.CharField(max_length=100)

    

    def __str__(self):

        return self.name

    

    class Meta:

        verbose_name_plural = "Universities"





class Candidate(models.Model):

    # Status choices

    DRAFT = 'Draft'

    MISSING_DOCS = 'Missing_Docs'

    VALIDATED = 'Validated'

    APPROVED = 'Approved'

    REJECTED = 'Rejected'

    

    STATUS_CHOICES = [

        (DRAFT, 'Draft (Saved)'),

        (MISSING_DOCS, 'Missing Documents'),

        (VALIDATED, 'Validated - Ready for Farm Assignment'),

        (APPROVED, 'Approved'),

        (REJECTED, 'Rejected'),

    ]

    

    # Basic information

    passport_number = models.CharField(max_length=20, blank=True)  # Allow blank for incomplete profiles

    first_name = models.CharField(max_length=100, blank=True, default='')  # Allow blank for incomplete profiles

    last_name = models.CharField(max_length=100, blank=True, default='')  # Allow blank for incomplete profiles

    email = models.EmailField(blank=True, null=True)

    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Phone Number")

    address = models.TextField(blank=True, null=True, verbose_name="Address")

    

    # Personal details

    date_of_birth = models.DateField(blank=True, null=True)  # Allow null for incomplete profiles

    country_of_birth = models.CharField(max_length=100, blank=True)  # Allow blank for incomplete profiles

    nationality = models.CharField(max_length=100, blank=True)  # Allow blank for incomplete profiles

    religion = models.CharField(max_length=100, blank=True, null=True)

    

    # Family information

    father_name = models.CharField(max_length=100, blank=True, null=True)

    mother_name = models.CharField(max_length=100, blank=True, null=True)

    

    # Passport details

    passport_issue_date = models.DateField(blank=True, null=True)  # Allow null for incomplete profiles

    passport_expiry_date = models.DateField(blank=True, null=True)  # Allow null for incomplete profiles

    place_of_issue = models.CharField(max_length=100, blank=True, null=True, verbose_name="Place of Issue")

    

    GENDER_CHOICES = [

        ('Male', 'Male'),

        ('Female', 'Female'),

        ('Other', 'Other'),

    ]

    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)  # Allow blank for incomplete profiles

    shoes_size = models.CharField(max_length=10, blank=True, null=True)

    shirt_size = models.CharField(max_length=10, blank=True, null=True)

    

    # Education details

    EDUCATION_LEVEL_CHOICES = [

        ('high_school', 'High School'),

        ('bachelor', "Bachelor's Degree"),

        ('master', "Master's Degree"),

        ('phd', 'PhD'),

        ('other', 'Other'),

    ]

    university = models.CharField(max_length=200, blank=True, null=True, verbose_name="University")

    year_graduated = models.IntegerField(blank=True, null=True)

    highest_education_level = models.CharField(max_length=20, choices=EDUCATION_LEVEL_CHOICES, blank=True, null=True, verbose_name="Highest Education Level")

    field_of_study = models.CharField(max_length=100, blank=True, null=True, verbose_name="Field of Study")

    graduation_year = models.IntegerField(blank=True, null=True, verbose_name="Graduation Year")

    specialization = models.CharField(max_length=100, blank=True)  # Allow blank for incomplete profiles

    secondary_specialization = models.CharField(max_length=100, blank=True, null=True)

    

    # Additional information

    SMOKING_CHOICES = [

        ('Never', 'Never'),

        ('Sometimes', 'Sometimes'),

        ('Often', 'Often'),

    ]

    smokes = models.CharField(max_length=10, choices=SMOKING_CHOICES, default='Never')

    

    # Job experience

    job_experience = models.TextField(

        blank=True, 

        null=True, 

        verbose_name="Job Experience",

        help_text="Describe your relevant work/job experience"

    )

    

    # Program association

    program = models.ForeignKey(AgricultureProgram, on_delete=models.SET_NULL, null=True, blank=True, related_name='candidates')

    

    # Status and registration

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=DRAFT)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    

    # Personal Information

    middle_initial = models.CharField(max_length=5, blank=True, null=True, verbose_name="Middle Initial")

    

    HEALTH_CHOICES = [

        ('Excellent', 'Excellent'),

        ('Fair', 'Fair'),

        ('Poor', 'Poor'),

    ]

    health_condition = models.CharField(max_length=20, choices=HEALTH_CHOICES, blank=True, null=True, verbose_name="Health Condition")

    health_remarks = models.TextField(blank=True, null=True, verbose_name="Health Remarks")

    

    # Files

    profile_image = models.ImageField(upload_to='candidate_images/', blank=True, null=True, verbose_name="Profile Image")

    license_scan = models.FileField(upload_to='candidate_licenses/', blank=True, null=True, verbose_name="License Scan")

    passport_scan = models.FileField(upload_to='passports/', blank=True, null=True, verbose_name="Passport Scan")

    academic_certificate = models.FileField(upload_to='candidate_certificates/', blank=True, null=True, verbose_name="Academic Certificate")

    tor = models.FileField(upload_to='documents/tor/', blank=True, null=True, verbose_name="Transcript of Records (TOR)")

    nc2_tesda = models.FileField(upload_to='documents/tesda/', blank=True, null=True, verbose_name="NC2 from TESDA")

    diploma = models.FileField(upload_to='documents/diploma/', blank=True, null=True, verbose_name="Diploma")

    good_moral = models.FileField(upload_to='documents/moral/', blank=True, null=True, verbose_name="Good Moral Character")

    nbi_clearance = models.FileField(upload_to='documents/nbi/', blank=True, null=True, verbose_name="NBI Clearance")

    

    # Document deadline for missing documents

    document_deadline = models.DateTimeField(blank=True, null=True, verbose_name="Document Upload Deadline",

        help_text="Deadline for applicant to upload missing documents")

    missing_documents_note = models.TextField(blank=True, verbose_name="Missing Documents/Fields",

        help_text="List of missing documents or required fields")

    

    # Farm assignment (only after validation)

    assigned_farm = models.CharField(max_length=200, blank=True, verbose_name="Assigned Farm Location")

    farm_assignment_date = models.DateField(blank=True, null=True, verbose_name="Farm Assignment Date")

    

    # System fields

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_candidates')

    

    def __str__(self):

        return f"{self.first_name} {self.last_name} ({self.passport_number})"

    @property
    def full_name_last_first(self):
        mi = f" {self.middle_initial}." if hasattr(self, 'middle_initial') and self.middle_initial else ""
        if self.last_name and self.first_name:
            return f"{self.last_name}, {self.first_name}{mi}"
        elif self.last_name:
            return self.last_name
        elif self.first_name:
            return f"{self.first_name}{mi}"
        return "--"

    

    class Meta:

        # Removed unique_together constraint to allow flexible applications with incomplete profiles

        # Users can now apply and complete their information later

        # unique_together = ('passport_number', 'university')

        pass

    

    def validate_application(self, deadline_days=7, save=True):

        """

        Validate the application for completeness before farm assignment.

        Returns tuple: (is_valid, missing_items_list)

        

        Criteria:

        1. If all DOCUMENTS and required FIELDS are complete, status = APPROVED.

        2. If all required DOCUMENTS are complete but FIELDS are missing, status = VALIDATED.

        3. If required DOCUMENTS are missing, status = MISSING_DOCS and document_deadline is set.

        """

        from django.utils import timezone

        from datetime import timedelta

        

        missing_docs = []

        missing_fields = []

        

        # 1. Check Required Documents

        if not self.passport_scan:

            missing_docs.append("Passport Scan")

        if not self.tor:

            missing_docs.append("Transcript of Records (TOR)")

        if not self.diploma:

            missing_docs.append("Diploma")

        if not self.good_moral:

            missing_docs.append("Good Moral Character Certificate")

        if not self.nbi_clearance:

            missing_docs.append("NBI Clearance")

        if not self.profile_image:

            missing_docs.append("Profile Photograph")

            

        # Check if program requires license

        if self.program and self.program.requires_license and not self.license_scan:

            missing_docs.append("Driver's License (Required for this program)")

            

        # 2. Check Required Personal Fields

        personal_required = {

            'first_name': "First Name",

            'last_name': "Last Name",

            'email': "Email Address",

            'phone_number': "Phone Number",

            'address': "Home Address",

            'date_of_birth': "Date of Birth",

            'gender': "Gender / Sex",

            'nationality': "Nationality",

            'health_condition': "Health Condition",

            'shirt_size': "Shirt Size",

            'shoes_size': "Shoes Size",

            'university': "University",

            'field_of_study': "Course / Field of Study",

            'specialization': "Primary Specialization",

            'graduation_year': "Graduation Year",

            'passport_number': "Passport Number",

            'passport_issue_date': "Passport Issue Date",

            'passport_expiry_date': "Passport Expiry Date",

            'place_of_issue': "Passport Place of Issue"

        }

        

        for field, label in personal_required.items():

            value = getattr(self, field)

            if not value:

                missing_fields.append(label)

        

        docs_complete = len(missing_docs) == 0

        fields_complete = len(missing_fields) == 0

        is_fully_complete = docs_complete and fields_complete

        

        # If read-only validation requested (e.g. GET edit page), return completeness without modifying DB or mutating status
        if not save:
            return is_fully_complete, missing_docs + missing_fields

        # Decide status based on completeness

        if is_fully_complete:

            # Full completion: Auto-Approve!

            self.status = self.APPROVED

            self.missing_documents_note = ""

            self.document_deadline = None

        elif docs_complete:

            # Documents are done but fields are missing: VALIDATED

            self.status = self.VALIDATED

            self.missing_documents_note = "Required fields missing: " + ", ".join(missing_fields)

            self.document_deadline = None

        else:

            # Documents are missing: MISSING_DOCS

            self.status = self.MISSING_DOCS

            all_missing = missing_docs + missing_fields

            self.missing_documents_note = "Missing: " + ", ".join(all_missing)

            if not self.document_deadline:  # Only set deadline if not already set

                self.document_deadline = timezone.now() + timedelta(days=deadline_days)

        

        self.save()

        return is_fully_complete, missing_docs + missing_fields

    

    def is_deadline_passed(self):

        """Check if document deadline has passed"""

        from django.utils import timezone

        if self.document_deadline:

            return timezone.now() > self.document_deadline

        return False

    

    def days_until_deadline(self):

        """Get days remaining until deadline"""

        from django.utils import timezone

        if self.document_deadline:

            delta = self.document_deadline - timezone.now()

            return max(0, delta.days)

        return None

    

    def can_assign_farm(self):
        """Check if candidate is validated and ready for farm assignment"""
        return self.status == self.VALIDATED


class CandidateStatusHistory(models.Model):
    """Chronological record of status transitions for a candidate's application."""

    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name='status_history'
    )
    status = models.CharField(
        max_length=20,
        choices=Candidate.STATUS_CHOICES,
        help_text="Status after transition"
    )
    from_status = models.CharField(
        max_length=20,
        choices=Candidate.STATUS_CHOICES,
        blank=True,
        null=True,
        help_text="Status prior to transition (None for initial creation)"
    )
    timestamp = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        help_text="When transition occurred"
    )
    missing_documents_note = models.TextField(
        blank=True,
        default='',
        help_text="Snapshot of missing documents note at transition"
    )
    document_deadline = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Snapshot of document deadline at transition"
    )
    notes = models.TextField(
        blank=True,
        default='',
        help_text="Optional candidate-safe notes"
    )

    class Meta:
        ordering = ['timestamp', 'id']
        indexes = [
            models.Index(fields=['candidate', 'timestamp']),
        ]
        verbose_name = 'Candidate Status History'
        verbose_name_plural = 'Candidate Status Histories'

    def __str__(self):
        return f"Candidate #{self.candidate_id}: {self.from_status or 'Initial'} -> {self.status} at {self.timestamp:%Y-%m-%d %H:%M}"


class Notification(models.Model):

    """Notification model for user alerts"""

    # Types of notifications

    INFO = 'info'

    SUCCESS = 'success'

    WARNING = 'warning'

    ERROR = 'error'

    

    NOTIFICATION_TYPES = [

        (INFO, 'Information'),

        (SUCCESS, 'Success'),

        (WARNING, 'Warning'),

        (ERROR, 'Error'),

    ]

    

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')

    message = models.TextField()

    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES, default=INFO)

    link = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    read = models.BooleanField(default=False)

    

    class Meta:

        ordering = ['-created_at']

    

    def __str__(self):

        return f"{self.user.username} - {self.message[:30]}..."

        

    @classmethod

    def add_notification(cls, user, message, notification_type=INFO, link=None):

        """Utility method to create a notification"""

        return cls.objects.create(

            user=user,

            message=message,

            notification_type=notification_type,

            link=link

        )



    @classmethod

    def clear_old_notifications(cls, user, days=30):

        """Remove notifications older than the specified number of days"""

        from datetime import timedelta

        from django.utils import timezone

        cutoff_date = timezone.now() - timedelta(days=days)

        return cls.objects.filter(user=user, created_at__lt=cutoff_date).delete()





class ActivityLog(models.Model):

    """Generic activity and audit log for all user/system actions."""

    ACTION_CREATE = 'CREATE'

    ACTION_UPDATE = 'UPDATE'

    ACTION_DELETE = 'DELETE'

    ACTION_LOGIN = 'LOGIN'

    ACTION_LOGOUT = 'LOGOUT'

    ACTION_FAILED_LOGIN = 'FAILED_LOGIN'

    ACTION_SYSTEM = 'SYSTEM'



    ACTION_CHOICES = [

        (ACTION_CREATE, 'Create'),

        (ACTION_UPDATE, 'Update'),

        (ACTION_DELETE, 'Delete'),

        (ACTION_LOGIN, 'Login'),

        (ACTION_LOGOUT, 'Logout'),

        (ACTION_FAILED_LOGIN, 'Failed Login'),

        (ACTION_SYSTEM, 'System'),

    ]



    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES)

    # Model label in app_label.ModelName form, e.g. "core.Candidate"

    model_name = models.CharField(max_length=100, db_index=True)

    object_id = models.CharField(max_length=64, blank=True, null=True)

    before_data = models.JSONField(encoder=DjangoJSONEncoder, blank=True, null=True)

    after_data = models.JSONField(encoder=DjangoJSONEncoder, blank=True, null=True)

    ip_address = models.GenericIPAddressField(blank=True, null=True)

    session_key = models.CharField(max_length=40, blank=True, null=True)

    timestamp = models.DateTimeField(default=timezone.now, db_index=True)



    class Meta:

        ordering = ['-timestamp']

        indexes = [

            models.Index(fields=['user']),

            models.Index(fields=['action_type']),

            models.Index(fields=['timestamp']),

        ]



    def __str__(self):  # pragma: no cover

        return f"{self.timestamp:%Y-%m-%d %H:%M:%S} {self.action_type} {self.model_name}#{self.object_id}"



    @staticmethod

    def model_from_label(label: str):

        try:

            return apps.get_model(label)

        except Exception:

            return None



    def rollback(self):

        """Rollback the target object to the 'before_data' snapshot.

        Returns the saved instance or None if not possible.

        """

        Model = self.model_from_label(self.model_name)

        if not Model or not self.object_id or not self.before_data:

            return None

        try:

            with transaction.atomic():

                instance = Model.objects.get(pk=self.object_id)

                for field, value in self.before_data.items():

                    # Only assign concrete editable fields

                    try:

                        f = Model._meta.get_field(field)

                        if getattr(f, 'editable', True):

                            setattr(instance, field, value)

                    except Exception:

                        continue

                instance.save()

                return instance

        except Model.DoesNotExist:

            return None





class UploadedFile(models.Model):

    """Track all uploaded files with metadata to prevent duplicates and manage file integrity."""

    

    # Document type choices - maps to the field names in Profile, Registration, Candidate models

    DOCUMENT_TYPES = [

        ('profile_image', 'Profile Image'),

        ('license_scan', 'License Scan'),

        ('passport_scan', 'Passport Scan'),

        ('academic_certificate', 'Academic Certificate'),

        ('tor', 'Transcript of Records (TOR)'),

        ('nc2_tesda', 'NC2 from TESDA'),

        ('diploma', 'Diploma'),

        ('good_moral', 'Good Moral Character'),

        ('nbi_clearance', 'NBI Clearance'),

    ]

    

    # User who uploaded the file

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_files', db_index=True)

    

    # Document type/field name

    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES, db_index=True)

    

    # File metadata

    file_name = models.CharField(max_length=255, help_text="Original filename")

    file_path = models.CharField(max_length=500, help_text="Path to the file in storage")

    file_size = models.PositiveIntegerField(help_text="File size in bytes")

    file_hash = models.CharField(max_length=64, db_index=True, help_text="SHA-256 hash of file content")

    mime_type = models.CharField(max_length=100, blank=True, null=True)

    

    # Model reference - which model instance this file is attached to

    model_name = models.CharField(max_length=50, help_text="Model name: Profile, Registration, or Candidate")

    model_id = models.PositiveIntegerField(help_text="ID of the model instance")

    

    # Timestamps

    uploaded_at = models.DateTimeField(auto_now_add=True, db_index=True)

    updated_at = models.DateTimeField(auto_now=True)

    

    # Status

    is_active = models.BooleanField(default=True, help_text="False if file has been replaced or deleted")

    

    class Meta:

        ordering = ['-uploaded_at']

        indexes = [

            models.Index(fields=['user', 'document_type']),

            models.Index(fields=['user', 'file_hash']),

            models.Index(fields=['file_hash']),

        ]

        # Prevent duplicate uploads: same user can't upload same file hash to same document type

        unique_together = [['user', 'document_type', 'file_hash']]

    

    def __str__(self):

        return f"{self.user.username} - {self.get_document_type_display()} - {self.file_name}"

    

    @staticmethod

    def calculate_file_hash(file_obj):

        """Calculate SHA-256 hash of a file object."""

        hasher = hashlib.sha256()

        

        # Reset file pointer to beginning

        if hasattr(file_obj, 'seek'):

            file_obj.seek(0)

        

        # Read and hash file in chunks for memory efficiency

        for chunk in file_obj.chunks():

            hasher.update(chunk)

        

        # Reset file pointer again for subsequent operations

        if hasattr(file_obj, 'seek'):

            file_obj.seek(0)

        

        return hasher.hexdigest()

    

    @classmethod

    def check_duplicate_upload(cls, user, document_type, file_obj):

        """

        Check if user is trying to upload a file they've already uploaded to ANY document field.

        Returns tuple: (is_duplicate, existing_upload, error_message)

        """

        file_hash = cls.calculate_file_hash(file_obj)

        

        # Check if this exact file (by hash) has been uploaded by this user to ANY field

        existing_upload = cls.objects.filter(

            user=user,

            file_hash=file_hash,

            is_active=True

        ).exclude(

            document_type=document_type  # Allow re-uploading to same field

        ).first()

        

        if existing_upload:

            error_msg = (

                f"This file has already been uploaded as your {existing_upload.get_document_type_display()}. "

                f"Each document must be unique. Please upload a different file."

            )

            return True, existing_upload, error_msg

        

        # Check if user already has a file uploaded for this specific document type

        existing_doc = cls.objects.filter(

            user=user,

            document_type=document_type,

            is_active=True

        ).first()

        

        if existing_doc and existing_doc.file_hash != file_hash:

            # User is replacing an existing document with a new one - this is allowed

            return False, existing_doc, None

        

        return False, None, None

    

    @classmethod

    def register_upload(cls, user, document_type, file_obj, model_name, model_id):

        """

        Register a new file upload or update existing record.

        Uses get_or_create to avoid unique constraint violations.

        """

        if hasattr(file_obj, 'seek'):

            file_obj.seek(0)

            

        file_hash = cls.calculate_file_hash(file_obj)

        

        if hasattr(file_obj, 'seek'):

            file_obj.seek(0)

            

        file_name = getattr(file_obj, 'name', 'unknown')

        file_size = getattr(file_obj, 'size', 0)

        file_path = getattr(file_obj, 'name', '')

        

        # Get MIME type if available

        mime_type = getattr(file_obj, 'content_type', None)

        

        # Deactivate any existing uploads for this user and document type with DIFFERENT hash

        cls.objects.filter(

            user=user,

            document_type=document_type,

            is_active=True

        ).exclude(file_hash=file_hash).update(is_active=False)

        

        # Get or create the record (avoids duplicate hash error)

        uploaded_file, created = cls.objects.get_or_create(

            user=user,

            document_type=document_type,

            file_hash=file_hash,

            defaults={

                'file_name': file_name,

                'file_path': file_path,

                'file_size': file_size,

                'mime_type': mime_type,

                'model_name': model_name,

                'model_id': model_id,

                'is_active': True

            }

        )

        

        # If record already existed, update it

        if not created:

            uploaded_file.file_name = file_name

            uploaded_file.file_path = file_path

            uploaded_file.file_size = file_size

            uploaded_file.mime_type = mime_type

            uploaded_file.model_name = model_name

            uploaded_file.model_id = model_id

            uploaded_file.is_active = True

            uploaded_file.save()

        

        return uploaded_file

    

    @classmethod

    def get_user_documents(cls, user, active_only=True):

        """Get all documents uploaded by a user."""

        queryset = cls.objects.filter(user=user)

        if active_only:

            queryset = queryset.filter(is_active=True)

        return queryset.order_by('document_type', '-uploaded_at')

    

    @classmethod

    def cleanup_orphaned_records(cls):

        """Remove records for files that no longer exist in storage."""

        from django.conf import settings

        count = 0

        

        for record in cls.objects.filter(is_active=True):

            file_path = os.path.join(settings.MEDIA_ROOT, record.file_path)

            if not os.path.exists(file_path):

                record.is_active = False

                record.save()

                count += 1

        

        return count

