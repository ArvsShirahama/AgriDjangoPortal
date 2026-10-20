from django import forms

from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth.models import User

from django.core.exceptions import ValidationError

from django.core.validators import RegexValidator

from django.conf import settings

from django.utils import timezone

from .models import Profile, Registration, Candidate, University, UploadedFile

import os





class UserRegisterForm(UserCreationForm):

    email = forms.EmailField()

    first_name = forms.CharField(max_length=30)

    last_name = forms.CharField(max_length=30)

    

    class Meta:

        model = User

        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

        

    def __init__(self, *args, **kwargs):

        super(UserRegisterForm, self).__init__(*args, **kwargs)

        # Set form control classes for Bootstrap styling

        for field_name in self.fields:

            self.fields[field_name].widget.attrs.update({

                'class': 'form-control',

                'placeholder': f'Choose a {field_name.replace("_", " ")}' if "password" in field_name else f'Enter your {field_name.replace("_", " ")}'

            })





class AdminRegistrationForm(UserCreationForm):

    email = forms.EmailField()

    first_name = forms.CharField(max_length=30)

    last_name = forms.CharField(max_length=30)

    admin_code = forms.CharField(max_length=50)

    

    class Meta:

        model = User

        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'admin_code']

    

    def __init__(self, *args, **kwargs):

        super(AdminRegistrationForm, self).__init__(*args, **kwargs)

        # Set form control classes for Bootstrap styling

        for field_name in self.fields:

            self.fields[field_name].widget.attrs.update({

                'class': 'form-control',

                'placeholder': f'Enter your admin registration code' if field_name == 'admin_code' 

                              else f'Choose a {field_name.replace("_", " ")}' if "password" in field_name 

                              else f'Enter your {field_name.replace("_", " ")}'

            })

    

    def clean_admin_code(self):

        """Validate the admin registration code"""

        code = self.cleaned_data.get('admin_code')

        # The admin code would normally be stored in settings or database

        # For demonstration, we'll use a hardcoded value that can be updated later

        valid_code = getattr(settings, 'ADMIN_REGISTRATION_CODE', 'ADMIN123')

        

        if code != valid_code:

            raise ValidationError('Invalid admin registration code. Please contact the system administrator.')

        

        return code

    

    def save(self, commit=True):

        user = super(AdminRegistrationForm, self).save(commit=False)

        user.is_staff = True  # Grant staff permissions

        user.is_superuser = True  # Grant superuser permissions

        

        if commit:

            user.save()

        

        return user





class UserUpdateForm(forms.ModelForm):

    email = forms.EmailField()

    

    class Meta:

        model = User

        fields = ['username', 'first_name', 'last_name', 'email']

    

    def __init__(self, *args, **kwargs):

        super(UserUpdateForm, self).__init__(*args, **kwargs)

        # Set form control classes for Bootstrap styling

        for field_name in self.fields:

            self.fields[field_name].widget.attrs.update({'class': 'form-control'})





class ProfileUpdateForm(forms.ModelForm):

    university = forms.ModelChoiceField(

        queryset=University.objects.all(),

        to_field_name="name",

        empty_label="Select University",

        required=False,

        widget=forms.Select(attrs={'class': 'form-control'})

    )

    class Meta:

        model = Profile

        fields = ['phone_number', 'profile_image',

                  'father_name', 'mother_name', 'middle_initial', 'date_of_birth', 'gender',

                  'country_of_birth', 'nationality', 'religion', 'has_international_license', 'license_scan',

                  'health_condition', 'health_remarks',

                  'address', 'passport_number', 'passport_issue_date', 'passport_expiry_date', 'place_of_issue',

                  'highest_education_level', 'graduation_year', 'field_of_study',

                  'university', 'specialization', 'secondary_specialization', 'year_graduated',

                  'smokes', 'shirt_size', 'shoes_size', 'job_experience',

                  'passport_scan', 'academic_certificate', 'tor', 'nc2_tesda', 'diploma', 'good_moral', 'nbi_clearance']

        widgets = {

            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your phone number'}),

            'father_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name of father'}),

            'mother_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name of mother'}),

            'middle_initial': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'M.I.'}),

            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),

            'gender': forms.Select(attrs={'class': 'form-control'}),

            'country_of_birth': forms.Select(attrs={'class': 'form-control'}),

            'nationality': forms.Select(attrs={'class': 'form-control'}),

            'religion': forms.TextInput(attrs={'class': 'form-control'}),

            'health_condition': forms.Select(attrs={'class': 'form-control'}),

            'health_remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Any remarks...'}),

            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),

            'passport_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter passport number'}),

            'passport_issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),

            'passport_expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),

            'place_of_issue': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Place of issue'}),

            'highest_education_level': forms.Select(attrs={'class': 'form-control'}),

            'graduation_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Graduation year'}),

            'field_of_study': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Course'}),

            'specialization': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Primary specialization'}),

            'secondary_specialization': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Secondary specialization'}),

            'year_graduated': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Year graduated'}),

            'smokes': forms.Select(attrs={'class': 'form-control'}),

            'shirt_size': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., S, M, L, XL, XXL'}),

            'shoes_size': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 8, 9, 10, 42, 43'}),

            'job_experience': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe your relevant work/job experience...'}),

        }

    

    def __init__(self, *args, **kwargs):

        super(ProfileUpdateForm, self).__init__(*args, **kwargs)

        country_choices = [('', 'Select Country of Birth')] + [
            ('Philippines', 'Philippines'),
            ('Israel', 'Israel'),
            ('United States', 'United States'),
            ('Canada', 'Canada'),
            ('Australia', 'Australia'),
            ('United Kingdom', 'United Kingdom'),
            ('Japan', 'Japan'),
            ('Singapore', 'Singapore'),
            ('Thailand', 'Thailand'),
            ('Vietnam', 'Vietnam'),
            ('Malaysia', 'Malaysia'),
            ('Indonesia', 'Indonesia'),
            ('South Korea', 'South Korea'),
            ('China', 'China'),
            ('Taiwan', 'Taiwan'),
            ('India', 'India'),
            ('Saudi Arabia', 'Saudi Arabia'),
            ('United Arab Emirates', 'United Arab Emirates'),
            ('Qatar', 'Qatar'),
            ('Kuwait', 'Kuwait'),
            ('New Zealand', 'New Zealand'),
            ('Germany', 'Germany'),
            ('France', 'France'),
            ('Italy', 'Italy'),
            ('Spain', 'Spain'),
            ('Other', 'Other Country'),
        ]
        if self.instance and self.instance.country_of_birth:
            if not any(c[0] == self.instance.country_of_birth for c in country_choices):
                country_choices.append((self.instance.country_of_birth, self.instance.country_of_birth))
        self.fields['country_of_birth'].choices = country_choices

        nationality_choices = [('', 'Select Nationality')] + [
            ('Filipino', 'Filipino'),
            ('Israeli', 'Israeli'),
            ('American', 'American'),
            ('Canadian', 'Canadian'),
            ('Australian', 'Australian'),
            ('British', 'British'),
            ('Japanese', 'Japanese'),
            ('Singaporean', 'Singaporean'),
            ('Thai', 'Thai'),
            ('Vietnamese', 'Vietnamese'),
            ('Malaysian', 'Malaysian'),
            ('Indonesian', 'Indonesian'),
            ('Korean', 'Korean'),
            ('Chinese', 'Chinese'),
            ('Taiwanese', 'Taiwanese'),
            ('Indian', 'Indian'),
            ('Saudi', 'Saudi'),
            ('Emirati', 'Emirati'),
            ('Qatari', 'Qatari'),
            ('Kuwaiti', 'Kuwaiti'),
            ('New Zealander', 'New Zealander'),
            ('German', 'German'),
            ('French', 'French'),
            ('Italian', 'Italian'),
            ('Spanish', 'Spanish'),
            ('Other', 'Other Nationality'),
        ]
        if self.instance and self.instance.nationality:
            if not any(n[0] == self.instance.nationality for n in nationality_choices):
                nationality_choices.append((self.instance.nationality, self.instance.nationality))
        self.fields['nationality'].choices = nationality_choices



        # Set form control classes for Bootstrap styling

        self.fields['profile_image'].widget.attrs.update({

            'class': 'form-control',

            'accept': 'image/*'

        })

        self.fields['license_scan'].widget.attrs.update({

            'class': 'form-control',

            'accept': '.pdf,.jpg,.jpeg,.png'

        })



        # Set styling for new document fields

        document_fields = ['passport_scan', 'academic_certificate', 'tor', 'nc2_tesda', 'diploma', 'good_moral', 'nbi_clearance']

        for field_name in document_fields:

            if field_name in self.fields:

                self.fields[field_name].widget.attrs.update({

                    'class': 'form-control',

                    'accept': '.pdf,.jpg,.jpeg,.png'

                })



        # Set styling for new fields

        new_fields = ['address', 'passport_number', 'passport_issue_date', 'passport_expiry_date', 'place_of_issue',

                      'highest_education_level', 'graduation_year', 'field_of_study',

                      'university', 'specialization', 'secondary_specialization', 'year_graduated']

        for field_name in new_fields:

            if field_name in self.fields:

                if field_name in ['passport_issue_date', 'passport_expiry_date']:

                    self.fields[field_name].widget.attrs.update({

                        'class': 'form-control',

                        'type': 'date'

                    })

                elif field_name == 'graduation_year':

                    self.fields[field_name].widget.attrs.update({

                        'class': 'form-control',

                        'placeholder': 'Graduation year'

                    })

                elif field_name == 'year_graduated':

                    self.fields[field_name].widget.attrs.update({

                        'class': 'form-control',

                        'placeholder': 'Year graduated'

                    })

                elif field_name == 'highest_education_level':

                    self.fields[field_name].widget.attrs.update({

                        'class': 'form-control'

                    })

                else:

                    self.fields[field_name].widget.attrs.update({

                        'class': 'form-control'

                    })



        # Add phone number validation

        if 'phone_number' in self.fields:

            self.fields['phone_number'].validators = [RegexValidator(

                regex=r'^[\d\s\-\+\(\)\.]+$',

                message="Phone number can only contain numbers, spaces, dashes, plus signs, parentheses, and dots."

            )]

            self.fields['phone_number'].widget.attrs.update({

                'type': 'tel',

                'pattern': r'^[\d\s\-\+\(\)\.]+$',

                'placeholder': 'e.g., +63 912 345 6789',

                'title': 'Phone number can only contain numbers, spaces, dashes, plus signs, parentheses, and dots.'

            })

        

        # Mark important fields for program applications (frontend validation removed)

        # These fields are recommended but not strictly required

        # Users can apply and complete these fields later

        important_for_application = [

            'date_of_birth', 'gender', 'country_of_birth', 'nationality',

            'passport_number', 'passport_issue_date', 'passport_expiry_date',

            'university', 'specialization'

        ]

        

        for field_name in important_for_application:

            if field_name in self.fields:

                # Update help text to indicate importance (but not strict requirement)

                if not self.fields[field_name].help_text:

                    self.fields[field_name].help_text = 'Recommended for program applications'

        

    def clean_profile_image(self):

        profile_image = self.cleaned_data.get('profile_image')

        if profile_image:

            # Check file size (max 2MB)

            if profile_image.size > 2 * 1024 * 1024:

                raise ValidationError("Image size should not exceed 2MB")

            

            # Check file extension

            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']

            ext = os.path.splitext(profile_image.name)[1]

            if not ext.lower() in valid_extensions:

                raise ValidationError("Only JPG, JPEG, PNG and GIF files are allowed")

        

        return profile_image

        

    def clean_phone_number(self):

        phone_number = self.cleaned_data.get('phone_number')

        if phone_number:

            # Remove any non-digit characters

            phone_number = ''.join(filter(str.isdigit, phone_number))

            

            # Check if phone number has a valid length

            if len(phone_number) < 10 or len(phone_number) > 15:

                raise ValidationError("Please enter a valid phone number")

            

        return phone_number



    def clean_license_scan(self):

        from django.db.models.fields.files import FieldFile

        license_scan = self.cleaned_data.get('license_scan')

        if license_scan:

            validate_file_size(license_scan)

            validate_file_extension(license_scan, ['.pdf', '.jpg', '.jpeg', '.png'])

            # Check for duplicates across user's documents (only for NEW uploads)

            if self.instance and self.instance.user and not isinstance(license_scan, FieldFile):

                validate_no_duplicate(self.instance.user, 'license_scan', license_scan)

        return license_scan



    def clean_passport_scan(self):

        from django.db.models.fields.files import FieldFile

        passport_scan = self.cleaned_data.get('passport_scan')

        if passport_scan:

            validate_file_size(passport_scan)

            validate_file_extension(passport_scan, ['.pdf', '.jpg', '.jpeg', '.png'])

            # Check for duplicates across user's documents (only for NEW uploads)

            if self.instance and self.instance.user and not isinstance(passport_scan, FieldFile):

                validate_no_duplicate(self.instance.user, 'passport_scan', passport_scan)

        return passport_scan



    def clean_academic_certificate(self):

        from django.db.models.fields.files import FieldFile

        academic_certificate = self.cleaned_data.get('academic_certificate')

        if academic_certificate:

            validate_file_size(academic_certificate)

            validate_file_extension(academic_certificate, ['.pdf', '.jpg', '.jpeg', '.png'])

            # Check for duplicates across user's documents (only for NEW uploads)

            if self.instance and self.instance.user and not isinstance(academic_certificate, FieldFile):

                validate_no_duplicate(self.instance.user, 'academic_certificate', academic_certificate)

        return academic_certificate



    def clean_tor(self):

        from django.db.models.fields.files import FieldFile

        tor = self.cleaned_data.get('tor')

        if tor:

            validate_file_size(tor)

            validate_file_extension(tor, ['.pdf', '.jpg', '.jpeg', '.png'])

            # Check for duplicates across user's documents (only for NEW uploads)

            if self.instance and self.instance.user and not isinstance(tor, FieldFile):

                validate_no_duplicate(self.instance.user, 'tor', tor)

        return tor



    def clean_nc2_tesda(self):

        from django.db.models.fields.files import FieldFile

        nc2_tesda = self.cleaned_data.get('nc2_tesda')

        if nc2_tesda:

            validate_file_size(nc2_tesda)

            validate_file_extension(nc2_tesda, ['.pdf', '.jpg', '.jpeg', '.png'])

            # Check for duplicates across user's documents (only for NEW uploads)

            if self.instance and self.instance.user and not isinstance(nc2_tesda, FieldFile):

                validate_no_duplicate(self.instance.user, 'nc2_tesda', nc2_tesda)

        return nc2_tesda



    def clean_diploma(self):

        from django.db.models.fields.files import FieldFile

        diploma = self.cleaned_data.get('diploma')

        if diploma:

            validate_file_size(diploma)

            validate_file_extension(diploma, ['.pdf', '.jpg', '.jpeg', '.png'])

            # Check for duplicates across user's documents (only for NEW uploads)

            if self.instance and self.instance.user and not isinstance(diploma, FieldFile):

                validate_no_duplicate(self.instance.user, 'diploma', diploma)

        return diploma



    def clean_good_moral(self):

        from django.db.models.fields.files import FieldFile

        good_moral = self.cleaned_data.get('good_moral')

        if good_moral:

            validate_file_size(good_moral)

            validate_file_extension(good_moral, ['.pdf', '.jpg', '.jpeg', '.png'])

            # Check for duplicates across user's documents (only for NEW uploads)

            if self.instance and self.instance.user and not isinstance(good_moral, FieldFile):

                validate_no_duplicate(self.instance.user, 'good_moral', good_moral)

        return good_moral



    def clean_nbi_clearance(self):

        from django.db.models.fields.files import FieldFile

        nbi_clearance = self.cleaned_data.get('nbi_clearance')

        if nbi_clearance:

            validate_file_size(nbi_clearance)

            validate_file_extension(nbi_clearance, ['.pdf', '.jpg', '.jpeg', '.png'])

            # Check for duplicates across user's documents (only for NEW uploads)

            if self.instance and self.instance.user and not isinstance(nbi_clearance, FieldFile):

                validate_no_duplicate(self.instance.user, 'nbi_clearance', nbi_clearance)

        return nbi_clearance



    def clean(self):

        cleaned_data = super().clean()

        has_license = cleaned_data.get("has_international_license")

        license_scan = cleaned_data.get("license_scan")



        # Phone number validation

        phone_number = cleaned_data.get('phone_number')

        if phone_number:

            import re

            if not re.match(r'^[\d\s\-\+\(\)\.]+$', phone_number):

                self.add_error('phone_number', "Phone number can only contain numbers, spaces, dashes, plus signs, parentheses, and dots.")



        if has_license and not license_scan:

            self.add_error('license_scan', "Please upload a scan of your license to verify.")



        # Check for duplicate files within the same form submission

        from core.models import UploadedFile

        from django.db.models.fields.files import FieldFile

        

        document_fields = ['license_scan', 'passport_scan', 'academic_certificate', 

                          'tor', 'nc2_tesda', 'diploma', 'good_moral', 'nbi_clearance']

        

        # Calculate hashes for all uploaded files in this submission

        file_hashes = {}  # {field_name: hash}

        for field_name in document_fields:

            file_obj = cleaned_data.get(field_name)

            # Only check NEW uploads (not existing saved files)

            # FieldFile = existing file, anything else with chunks() = new upload

            if file_obj and hasattr(file_obj, 'chunks') and not isinstance(file_obj, FieldFile):

                # Calculate hash for this file

                if hasattr(file_obj, 'seek'):

                    file_obj.seek(0)

                file_hash = UploadedFile.calculate_file_hash(file_obj)

                if hasattr(file_obj, 'seek'):

                    file_obj.seek(0)

                

                # Check if this hash already appeared in another field

                for existing_field, existing_hash in file_hashes.items():

                    if existing_hash == file_hash:

                        # Get human-readable names

                        field_display = dict(UploadedFile.DOCUMENT_TYPES).get(field_name, field_name)

                        existing_display = dict(UploadedFile.DOCUMENT_TYPES).get(existing_field, existing_field)

                        

                        error_msg = (

                            f"You uploaded the same file to both '{existing_display}' and '{field_display}'. "

                            f"Each document must be unique. Please upload different files."

                        )

                        self.add_error(field_name, error_msg)

                        self.add_error(existing_field, error_msg)

                        break

                

                # Store this file's hash

                file_hashes[field_name] = file_hash



        return cleaned_data





def validate_file_size(value):

    """Validate file size (max 5MB)"""

    from django.db.models.fields.files import FieldFile

    

    # Skip validation for existing FieldFile objects where the file might be missing

    if isinstance(value, FieldFile):

        try:

            if not value.storage.exists(value.name):

                # File reference exists in DB but file is missing - skip validation

                return value

        except Exception:

            # If we can't check existence, skip validation to avoid crashes

            return value

    

    try:

        filesize = value.size

    except (FileNotFoundError, OSError):

        # File doesn't exist on disk - skip size validation

        return value

        

    if filesize > 5 * 1024 * 1024:  # 5MB

        raise ValidationError("The maximum file size that can be uploaded is 5MB")

    return value



def validate_file_extension(value, valid_extensions):

    """Validate file extension"""

    ext = os.path.splitext(value.name)[1]

    if not ext.lower() in valid_extensions:

        raise ValidationError(f"Only {', '.join(valid_extensions)} files are allowed")

    return value



def validate_pdf(value):

    """Validate that file is a PDF"""

    return validate_file_extension(value, ['.pdf'])





def is_missing_file(value):

    """Check if value is an existing FieldFile with missing physical file."""

    from django.db.models.fields.files import FieldFile

    if isinstance(value, FieldFile):

        try:

            return not value.storage.exists(value.name)

        except Exception:

            return True  # Assume missing if we can't check

    return False





def validate_no_duplicate(user, document_type, file_obj):

    """

    Validate that a file hasn't been uploaded to another document field by the same user.

    This prevents users from uploading the same file (e.g., NBI) to multiple different fields.

    """

    if not file_obj or not user or not user.is_authenticated:

        return file_obj

    

    is_duplicate, existing_upload, error_msg = UploadedFile.check_duplicate_upload(

        user, document_type, file_obj

    )

    

    if is_duplicate:

        raise ValidationError(error_msg)

    

    return file_obj





class ProgramRegistrationForm(forms.ModelForm):

    # Add file fields with validators

    tor = forms.FileField(

        validators=[validate_file_size],

        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),

        help_text="Upload your Transcript of Records (PDF/JPG/PNG, max 5MB)",

        required=False

    )

    

    nc2_tesda = forms.FileField(

        validators=[validate_file_size],

        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),

        help_text="Upload your NC2 from TESDA certificate (PDF/JPG/PNG, max 5MB)",

        required=False

    )

    

    good_moral = forms.FileField(

        validators=[validate_file_size],

        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),

        help_text="Upload your Good Moral Character certificate (PDF/JPG/PNG, max 5MB)",

        required=False

    )

    

    nbi_clearance = forms.FileField(

        validators=[validate_file_size],

        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),

        help_text="Upload your NBI Clearance (PDF/JPG/PNG, max 5MB)",

        required=False

    )

    

    class Meta:

        model = Registration

        fields = ['notes', 'tor', 'nc2_tesda', 'good_moral', 'nbi_clearance']

        widgets = {

            'notes': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Any additional information you want to provide...'}),

        }

    

    def __init__(self, *args, **kwargs):

        self.user = kwargs.pop('user', None)

        super().__init__(*args, **kwargs)

    

    def clean_tor(self):

        file = self.cleaned_data.get('tor')

        if file:

            validate_file_extension(file, ['.pdf', '.jpg', '.jpeg', '.png'])

            # Check for duplicates across user's documents

            if self.user:

                validate_no_duplicate(self.user, 'tor', file)

        return file

    

    def clean_nc2_tesda(self):

        file = self.cleaned_data.get('nc2_tesda')

        if file:

            validate_file_extension(file, ['.pdf', '.jpg', '.jpeg', '.png'])

            # Check for duplicates across user's documents

            if self.user:

                validate_no_duplicate(self.user, 'nc2_tesda', file)

        return file

    

    def clean_good_moral(self):

        file = self.cleaned_data.get('good_moral')

        if file:

            validate_file_extension(file, ['.pdf', '.jpg', '.jpeg', '.png'])

            # Check for duplicates across user's documents

            if self.user:

                validate_no_duplicate(self.user, 'good_moral', file)

        return file

    

    def clean_nbi_clearance(self):

        file = self.cleaned_data.get('nbi_clearance')

        if file:

            validate_file_extension(file, ['.pdf', '.jpg', '.jpeg', '.png'])

            # Check for duplicates across user's documents

            if self.user:

                validate_no_duplicate(self.user, 'nbi_clearance', file)

        return file





class CandidateForm(forms.ModelForm):

    """Form for adding/editing candidate information."""

    university = forms.ModelChoiceField(

        queryset=University.objects.all(),

        to_field_name="name",

        empty_label="Select University",

        required=False,

        widget=forms.Select(attrs={'class': 'form-control'})

    )

    

    class Meta:

        model = Candidate

        fields = [

            # Basic information

            'passport_number',

            'first_name',

            'middle_initial',

            'last_name',

            'email',

            'phone_number',

            'address',

            'date_of_birth', 'country_of_birth', 'nationality', 'religion',

            'gender',

            # Family information

            'father_name', 'mother_name',

            # Passport details

            'passport_issue_date', 'passport_expiry_date', 'place_of_issue',

            # Physical details

            'shoes_size', 'shirt_size',

            # Education details

            'university', 'highest_education_level', 'field_of_study', 'graduation_year', 'year_graduated',

            'specialization', 'secondary_specialization',

            # Additional information

            'health_condition', 'health_remarks',

            'smokes',

            'job_experience',

            # Program association

            'program',

            # Documents

            'profile_image', 'license_scan', 'passport_scan', 'academic_certificate',

            'tor', 'nc2_tesda', 'diploma', 'good_moral', 'nbi_clearance',

        ]

        widgets = {

            'passport_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Passport number'}),

            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),

            'middle_initial': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'M.I.'}),

            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Surname'}),

            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'}),

            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),

            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Home address'}),

            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),

            'country_of_birth': forms.Select(attrs={'class': 'form-control'}),

            'nationality': forms.Select(attrs={'class': 'form-control'}),

            'religion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Religion'}),

            'gender': forms.Select(attrs={'class': 'form-control'}),

            'health_condition': forms.Select(attrs={'class': 'form-control'}),

            'health_remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),

            'father_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Father's name"}),

            'mother_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Mother's name"}),

            'passport_issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),

            'passport_expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),

            'place_of_issue': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Place of issue'}),

            'shoes_size': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Shoes size'}),

            'shirt_size': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Shirt size'}),

            'highest_education_level': forms.Select(attrs={'class': 'form-control'}),

            'field_of_study': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Course'}),

            'graduation_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Graduation year'}),

            'year_graduated': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Year graduated'}),

            'specialization': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Primary specialization'}),

            'secondary_specialization': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Secondary specialization'}),

            'smokes': forms.Select(attrs={'class': 'form-control'}),

            'job_experience': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe your relevant work/job experience...'}),

            'program': forms.Select(attrs={'class': 'form-control'}),

            'profile_image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),

            'license_scan': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),

            'passport_scan': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),

            'academic_certificate': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),

            'tor': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),

            'nc2_tesda': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),

            'diploma': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),

            'good_moral': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),

            'nbi_clearance': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),

        }

    

    def __init__(self, *args, **kwargs):

        super(CandidateForm, self).__init__(*args, **kwargs)

        

        # Add country choices based on a predefined list

        self.fields['country_of_birth'].widget.choices = [('', 'Choose from list')] + [

            ('Philippines', 'Philippines'),

            ('Thailand', 'Thailand'),

            ('Vietnam', 'Vietnam'),

            # Add more countries as needed

        ]

        

        # Add nationality choices

        self.fields['nationality'].widget.choices = [('', 'Choose from list')] + [

            ('Filipino', 'Filipino'),

            ('Thai', 'Thai'),

            ('Vietnamese', 'Vietnamese'),

            ('Israeli', 'Israeli'),

            # Add more nationalities as needed

        ]

        

        # Populate program choices from database

        from core.models import University, AgricultureProgram

        programs = AgricultureProgram.objects.all().order_by('title')

        self.fields['program'].widget.choices = [('', 'Select Program (Optional)')] + [

            (prog.id, f"{prog.title} - {prog.location}") for prog in programs

        ]

        

        # Make some fields optional

        self.fields['program'].required = False

        self.fields['email'].required = False

        self.fields['religion'].required = False

        self.fields['father_name'].required = False

        self.fields['mother_name'].required = False

        self.fields['shoes_size'].required = False

        self.fields['shirt_size'].required = False

        self.fields['year_graduated'].required = False

        self.fields['secondary_specialization'].required = False

        self.fields['job_experience'].required = False

        

        # Make all document fields optional

        self.fields['passport_scan'].required = False

        self.fields['tor'].required = False

        self.fields['nc2_tesda'].required = False

        self.fields['diploma'].required = False

        self.fields['good_moral'].required = False

        self.fields['nbi_clearance'].required = False

    

    def clean(self):

        cleaned_data = super().clean()

        return cleaned_data



    # Add custom clean methods for file fields

    def clean_passport_scan(self):

        passport_scan = self.cleaned_data.get('passport_scan')

        if passport_scan and not is_missing_file(passport_scan):

            validate_file_size(passport_scan)

            validate_file_extension(passport_scan, ['.pdf', '.jpg', '.jpeg', '.png'])

            # For candidates created by staff, check against staff member's uploads

            if hasattr(self, 'created_by') and self.created_by:

                validate_no_duplicate(self.created_by, 'passport_scan', passport_scan)

        return passport_scan

        

    def clean_tor(self):

        tor = self.cleaned_data.get('tor')

        if tor and not is_missing_file(tor):

            validate_file_size(tor)

            validate_file_extension(tor, ['.pdf', '.jpg', '.jpeg', '.png'])

            # Check for duplicates

            if hasattr(self, 'created_by') and self.created_by:

                validate_no_duplicate(self.created_by, 'tor', tor)

        return tor

        

    def clean_nc2_tesda(self):

        nc2_tesda = self.cleaned_data.get('nc2_tesda')

        if nc2_tesda and not is_missing_file(nc2_tesda):

            validate_file_size(nc2_tesda)

            validate_file_extension(nc2_tesda, ['.pdf', '.jpg', '.jpeg', '.png'])

            # Check for duplicates

            if hasattr(self, 'created_by') and self.created_by:

                validate_no_duplicate(self.created_by, 'nc2_tesda', nc2_tesda)

        return nc2_tesda

        

    def clean_diploma(self):

        diploma = self.cleaned_data.get('diploma')

        if diploma and not is_missing_file(diploma):

            validate_file_size(diploma)

            validate_file_extension(diploma, ['.pdf', '.jpg', '.jpeg', '.png'])

            # Check for duplicates

            if hasattr(self, 'created_by') and self.created_by:

                validate_no_duplicate(self.created_by, 'diploma', diploma)

        return diploma

        

    def clean_good_moral(self):

        good_moral = self.cleaned_data.get('good_moral')

        if good_moral and not is_missing_file(good_moral):

            validate_file_size(good_moral)

            validate_file_extension(good_moral, ['.pdf', '.jpg', '.jpeg', '.png'])

            # Check for duplicates

            if hasattr(self, 'created_by') and self.created_by:

                validate_no_duplicate(self.created_by, 'good_moral', good_moral)

        return good_moral

        

    def clean_nbi_clearance(self):

        nbi_clearance = self.cleaned_data.get('nbi_clearance')

        if nbi_clearance and not is_missing_file(nbi_clearance):

            validate_file_size(nbi_clearance)

            validate_file_extension(nbi_clearance, ['.pdf', '.jpg', '.jpeg', '.png'])

            # Check for duplicates

            if hasattr(self, 'created_by') and self.created_by:

                validate_no_duplicate(self.created_by, 'nbi_clearance', nbi_clearance)

        return nbi_clearance





class CandidateSearchForm(forms.Form):

    """Form for searching candidates."""

    STATUSES = [

        ('', 'All statuses'),

        ('Draft', 'Draft'),

        ('Missing_Docs', 'Missing Documents'),

        ('Validated', 'Validated'),

        ('Approved', 'Approved'),

        ('Rejected', 'Rejected'),

    ]



    SEX_CHOICES = [

        ('', 'All sexes'),

        ('Male', 'Male'),

        ('Female', 'Female'),

        ('Other', 'Other'),

    ]



    SORT_CHOICES = [

        ('-created_at', 'Newest First'),

        ('created_at', 'Oldest First'),

        ('gender', 'Sex'),

        ('country_of_birth', 'Country'),

        ('nationality', 'Nationality'),

        ('status', 'Status'),

    ]



    # Search field

    search = forms.CharField(required=False, widget=forms.TextInput(attrs={

        'class': 'form-control', 

        'placeholder': 'Search by name or email...'

    }), label='Search')



    # Filter fields

    country = forms.CharField(required=False, widget=forms.Select(attrs={'class': 'form-control'}), label='Country')

    nationality = forms.CharField(required=False, widget=forms.Select(attrs={'class': 'form-control'}), label='Nationality')

    gender = forms.CharField(required=False, widget=forms.Select(choices=SEX_CHOICES, attrs={'class': 'form-control'}), label='Sex')

    specialization = forms.CharField(required=False, widget=forms.Select(attrs={'class': 'form-control'}), label='Specialization')

    status = forms.CharField(required=False, widget=forms.Select(choices=STATUSES, attrs={'class': 'form-control'}), label='Status')

    

    # Sorting field

    sort_by = forms.CharField(required=False, widget=forms.HiddenInput(), initial='-created_at')



    # Date range fields

    date_range = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': True, 'placeholder': 'Select date range'}), label='Date Range')

    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}), label='From Date')

    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}), label='To Date')

    

    def __init__(self, *args, **kwargs):

        super(CandidateSearchForm, self).__init__(*args, **kwargs)

        

        # Populate country choices

        self.fields['country'].widget.choices = [('', 'All countries')] + [

            ('Philippines', 'Philippines'),

            ('Thailand', 'Thailand'),

            ('Vietnam', 'Vietnam'),

            ('Sweden', 'Sweden'),

            ('Slovenia', 'Slovenia'),

            # Add more countries as needed

        ]



        # Populate nationality choices

        self.fields['nationality'].widget.choices = [('', 'All nationalities')] + [

            ('Filipino', 'Filipino'),

            ('Thai', 'Thai'),

            ('Vietnamese', 'Vietnamese'),

            ('Swedish', 'Swedish'),

            ('Slovenian', 'Slovenian'),

            # Add more nationalities as needed

        ]

        

        # Populate specialization choices

        self.fields['specialization'].widget.choices = [('', 'All specializations')] + [

            ('Animal science', 'Animal science'),

            ('Agronomy', 'Agronomy'),

            ('Horticulture', 'Horticulture'),

            ('Agricultural Engineering', 'Agricultural Engineering'),

            ('Press sub', 'Press sub'),

            ('Archaeologist', 'Archaeologist'),

            # Add more specializations as needed

        ]



class ProgramSearchForm(forms.Form):

    """Form for searching programs."""

    query = forms.CharField(

        required=False,

        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by keyword...'}), 

        label=""

    )

    country = forms.CharField(

        required=False,

        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Filter by country...'}), 

        label=""

    )

    location = forms.CharField(

        required=False,

        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Filter by location...'}), 

        label=""

    )

    gender = forms.ChoiceField(

        required=False,

        choices=[

            ('', 'All Sex'),

            ('Male', 'Male Only'),

            ('Female', 'Female Only'),

            ('Any', 'Any Sex')

        ],

        widget=forms.Select(attrs={'class': 'form-select'}),

        label=""

    )





class ComprehensiveRegisterForm(UserCreationForm):

    # User fields

    email = forms.EmailField(required=True)

    confirm_email = forms.EmailField(required=True, label='Confirm Email')

    

    # Profile fields (existing + new)

    middle_initial = forms.CharField(max_length=10, required=False, help_text="Middle Initial")

    religion = forms.CharField(max_length=100, required=False, help_text="Religion")

    age = forms.IntegerField(required=False, help_text="Age")

    country_of_birth = forms.CharField(max_length=100, required=False, help_text="Country of Birth")

    

    SMOKING_CHOICES = [('Yes', 'Yes'), ('No', 'No')]

    smoking_habits = forms.ChoiceField(choices=SMOKING_CHOICES, required=False, widget=forms.RadioSelect)

    

    shirt_size = forms.CharField(max_length=10, required=False, help_text="Shirt Size")

    shoe_size = forms.CharField(max_length=10, required=False, help_text="Shoe Size")

    

    university = forms.ModelChoiceField(

        queryset=University.objects.all(),

        to_field_name="name",

        empty_label="Select University",

        required=False,

        help_text="University"

    )

    primary_specialization = forms.CharField(max_length=100, required=False, help_text="Primary Specialization")

    secondary_specialization = forms.CharField(max_length=100, required=False, help_text="Secondary Specialization")

    phone_number = forms.CharField(

        max_length=20,

        required=False,

        help_text="Enter your phone number",

        validators=[RegexValidator(

            regex=r'^[\d\s\-\+\(\)\.]+$',

            message="Phone number can only contain numbers, spaces, dashes, plus signs, parentheses, and dots."

        )],

        widget=forms.TextInput(attrs={

            'type': 'tel',

            'pattern': r'[\d\s\-\+\(\)\.]+',

            'title': 'Phone number can only contain numbers and standard phone formatting characters',

            'oninput': "this.value = this.value.replace(/[^0-9\\s\\-\\+\\(\\)\\.]/g, '')"

        })

    )

    date_of_birth = forms.DateField(required=True, help_text="Enter your date of birth")

    gender = forms.ChoiceField(choices=Profile.GENDER_CHOICES, required=True)

    NATIONALITY_CHOICES = [

        ('', 'Select Nationality'),

        ('Afghan', 'Afghan'),

        ('Albanian', 'Albanian'),

        ('Algerian', 'Algerian'),

        ('American', 'American'),

        ('Andorran', 'Andorran'),

        ('Angolan', 'Angolan'),

        ('Antiguans', 'Antiguans'),

        ('Argentinean', 'Argentinean'),

        ('Armenian', 'Armenian'),

        ('Australian', 'Australian'),

        ('Austrian', 'Austrian'),

        ('Azerbaijani', 'Azerbaijani'),

        ('Bahamian', 'Bahamian'),

        ('Bahraini', 'Bahraini'),

        ('Bangladeshi', 'Bangladeshi'),

        ('Barbadian', 'Barbadian'),

        ('Barbudans', 'Barbudans'),

        ('Batswana', 'Batswana'),

        ('Belarusian', 'Belarusian'),

        ('Belgian', 'Belgian'),

        ('Belizean', 'Belizean'),

        ('Beninese', 'Beninese'),

        ('Bhutanese', 'Bhutanese'),

        ('Bolivian', 'Bolivian'),

        ('Bosnian', 'Bosnian'),

        ('Brazilian', 'Brazilian'),

        ('British', 'British'),

        ('Bruneian', 'Bruneian'),

        ('Bulgarian', 'Bulgarian'),

        ('Burkinabe', 'Burkinabe'),

        ('Burmese', 'Burmese'),

        ('Burundian', 'Burundian'),

        ('Cambodian', 'Cambodian'),

        ('Cameroonian', 'Cameroonian'),

        ('Canadian', 'Canadian'),

        ('Cape Verdean', 'Cape Verdean'),

        ('Central African', 'Central African'),

        ('Chadian', 'Chadian'),

        ('Chilean', 'Chilean'),

        ('Chinese', 'Chinese'),

        ('Colombian', 'Colombian'),

        ('Comoran', 'Comoran'),

        ('Congolese', 'Congolese'),

        ('Costa Rican', 'Costa Rican'),

        ('Croatian', 'Croatian'),

        ('Cuban', 'Cuban'),

        ('Cypriot', 'Cypriot'),

        ('Czech', 'Czech'),

        ('Danish', 'Danish'),

        ('Djibouti', 'Djibouti'),

        ('Dominican', 'Dominican'),

        ('Dutch', 'Dutch'),

        ('East Timorese', 'East Timorese'),

        ('Ecuadorean', 'Ecuadorean'),

        ('Egyptian', 'Egyptian'),

        ('Emirian', 'Emirian'),

        ('Equatorial Guinean', 'Equatorial Guinean'),

        ('Eritrean', 'Eritrean'),

        ('Estonian', 'Estonian'),

        ('Ethiopian', 'Ethiopian'),

        ('Fijian', 'Fijian'),

        ('Filipino', 'Filipino'),

        ('Finnish', 'Finnish'),

        ('French', 'French'),

        ('Gabonese', 'Gabonese'),

        ('Gambian', 'Gambian'),

        ('Georgian', 'Georgian'),

        ('German', 'German'),

        ('Ghanaian', 'Ghanaian'),

        ('Greek', 'Greek'),

        ('Grenadian', 'Grenadian'),

        ('Guatemalan', 'Guatemalan'),

        ('Guinea-Bissauan', 'Guinea-Bissauan'),

        ('Guinean', 'Guinean'),

        ('Guyanese', 'Guyanese'),

        ('Haitian', 'Haitian'),

        ('Herzegovinian', 'Herzegovinian'),

        ('Honduran', 'Honduran'),

        ('Hungarian', 'Hungarian'),

        ('I-Kiribati', 'I-Kiribati'),

        ('Icelander', 'Icelander'),

        ('Indian', 'Indian'),

        ('Indonesian', 'Indonesian'),

        ('Iranian', 'Iranian'),

        ('Iraqi', 'Iraqi'),

        ('Irish', 'Irish'),

        ('Israeli', 'Israeli'),

        ('Italian', 'Italian'),

        ('Ivorian', 'Ivorian'),

        ('Jamaican', 'Jamaican'),

        ('Japanese', 'Japanese'),

        ('Jordanian', 'Jordanian'),

        ('Kazakhstani', 'Kazakhstani'),

        ('Kenyan', 'Kenyan'),

        ('Kittian and Nevisian', 'Kittian and Nevisian'),

        ('Kuwaiti', 'Kuwaiti'),

        ('Kyrgyz', 'Kyrgyz'),

        ('Laotian', 'Laotian'),

        ('Latvian', 'Latvian'),

        ('Lebanese', 'Lebanese'),

        ('Liberian', 'Liberian'),

        ('Libyan', 'Libyan'),

        ('Liechtensteiner', 'Liechtensteiner'),

        ('Lithuanian', 'Lithuanian'),

        ('Luxembourgish', 'Luxembourgish'),

        ('Macedonian', 'Macedonian'),

        ('Malagasy', 'Malagasy'),

        ('Malawian', 'Malawian'),

        ('Malaysian', 'Malaysian'),

        ('Maldivan', 'Maldivan'),

        ('Malian', 'Malian'),

        ('Maltese', 'Maltese'),

        ('Marshallese', 'Marshallese'),

        ('Mauritanian', 'Mauritanian'),

        ('Mauritian', 'Mauritian'),

        ('Mexican', 'Mexican'),

        ('Micronesian', 'Micronesian'),

        ('Moldovan', 'Moldovan'),

        ('Monacan', 'Monacan'),

        ('Mongolian', 'Mongolian'),

        ('Moroccan', 'Moroccan'),

        ('Mosotho', 'Mosotho'),

        ('Motswana', 'Motswana'),

        ('Mozambican', 'Mozambican'),

        ('Namibian', 'Namibian'),

        ('Nauruan', 'Nauruan'),

        ('Nepalese', 'Nepalese'),

        ('New Zealander', 'New Zealander'),

        ('Nicaraguan', 'Nicaraguan'),

        ('Nigerian', 'Nigerian'),

        ('Nigerien', 'Nigerien'),

        ('North Korean', 'North Korean'),

        ('Northern Irish', 'Northern Irish'),

        ('Norwegian', 'Norwegian'),

        ('Omani', 'Omani'),

        ('Pakistani', 'Pakistani'),

        ('Palauan', 'Palauan'),

        ('Panamanian', 'Panamanian'),

        ('Papua New Guinean', 'Papua New Guinean'),

        ('Paraguayan', 'Paraguayan'),

        ('Peruvian', 'Peruvian'),

        ('Polish', 'Polish'),

        ('Portuguese', 'Portuguese'),

        ('Qatari', 'Qatari'),

        ('Romanian', 'Romanian'),

        ('Russian', 'Russian'),

        ('Rwandan', 'Rwandan'),

        ('Saint Lucian', 'Saint Lucian'),

        ('Salvadoran', 'Salvadoran'),

        ('Samoan', 'Samoan'),

        ('San Marinese', 'San Marinese'),

        ('Sao Tomean', 'Sao Tomean'),

        ('Saudi', 'Saudi'),

        ('Scottish', 'Scottish'),

        ('Senegalese', 'Senegalese'),

        ('Serbian', 'Serbian'),

        ('Seychellois', 'Seychellois'),

        ('Sierra Leonean', 'Sierra Leonean'),

        ('Singaporean', 'Singaporean'),

        ('Slovakian', 'Slovakian'),

        ('Slovenian', 'Slovenian'),

        ('Solomon Islander', 'Solomon Islander'),

        ('Somali', 'Somali'),

        ('South African', 'South African'),

        ('South Korean', 'South Korean'),

        ('Spanish', 'Spanish'),

        ('Sri Lankan', 'Sri Lankan'),

        ('Sudanese', 'Sudanese'),

        ('Surinamer', 'Surinamer'),

        ('Swazi', 'Swazi'),

        ('Swedish', 'Swedish'),

        ('Swiss', 'Swiss'),

        ('Syrian', 'Syrian'),

        ('Taiwanese', 'Taiwanese'),

        ('Tajik', 'Tajik'),

        ('Tanzanian', 'Tanzanian'),

        ('Thai', 'Thai'),

        ('Togolese', 'Togolese'),

        ('Tongan', 'Tongan'),

        ('Trinidadian or Tobagonian', 'Trinidadian or Tobagonian'),

        ('Tunisian', 'Tunisian'),

        ('Turkish', 'Turkish'),

        ('Tuvaluan', 'Tuvaluan'),

        ('Ugandan', 'Ugandan'),

        ('Ukrainian', 'Ukrainian'),

        ('Uruguayan', 'Uruguayan'),

        ('Uzbekistani', 'Uzbekistani'),

        ('Venezuelan', 'Venezuelan'),

        ('Vietnamese', 'Vietnamese'),

        ('Welsh', 'Welsh'),

        ('Yemenite', 'Yemenite'),

        ('Zambian', 'Zambian'),

        ('Zimbabwean', 'Zimbabwean'),

    ]

    nationality = forms.ChoiceField(choices=NATIONALITY_CHOICES, required=True, help_text="Select your nationality")

    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False, help_text="Enter your full address")

    

    # Passport fields

    passport_number = forms.CharField(max_length=20, required=True, help_text="Enter your passport number")

    confirm_passport_number = forms.CharField(max_length=20, required=True, help_text="Confirm passport number")

    passport_issue_date = forms.DateField(required=True, help_text="Passport issue date")

    passport_expiry_date = forms.DateField(required=True, help_text="Passport expiry date")

    place_of_issue = forms.CharField(max_length=100, required=False, help_text="Place of issue")

    

    # Academic fields

    highest_education_level = forms.ChoiceField(choices=Profile.EDUCATION_LEVEL_CHOICES, required=True)

    graduation_year = forms.IntegerField(required=True, min_value=1900, max_value=timezone.now().year, help_text="Year of graduation")

    year_graduated = forms.IntegerField(required=False, min_value=1900, max_value=timezone.now().year, help_text="Year graduated")

    field_of_study = forms.CharField(max_length=100, required=True, help_text="Field of study")

    

    # Additional fields

    preferred_country = forms.CharField(max_length=100, required=False, help_text="Preferred country for opportunities")

    willing_to_relocate = forms.BooleanField(required=False, initial=True, help_text="Are you willing to relocate?")

    special_requirements = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False, help_text="Any special requirements or notes")

    

    # Documents

    profile_image = forms.ImageField(required=False, help_text="Upload your profile photo (optional)")

    passport_scan = forms.FileField(required=False, help_text="Upload passport scan (PDF/JPG/PNG, max 5MB)")

    tor = forms.FileField(required=False, help_text="Upload Transcript of Records (PDF/JPG/PNG, max 5MB)")

    diploma = forms.FileField(required=False, help_text="Upload Diploma (PDF/JPG/PNG, max 5MB)")

    good_moral = forms.FileField(required=False, help_text="Upload Good Moral Character Certificate (PDF/JPG/PNG, max 5MB)")

    nbi_clearance = forms.FileField(required=False, help_text="Upload NBI Clearance (PDF/JPG/PNG, max 5MB)")

    license_scan = forms.FileField(required=False, help_text="Upload Driver's License (PDF/JPG/PNG, max 5MB)")

    nc2_tesda = forms.FileField(required=False, help_text="Upload NC2 TESDA Certificate (PDF/JPG/PNG, max 5MB)")

    academic_certificate = forms.FileField(required=False, help_text="Upload other academic certificates (PDF/JPG/PNG, max 5MB)")

    

    class Meta:

        model = User

        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # Bootstrap styling for all fields

        for field_name in self.fields:

            if isinstance(self.fields[field_name], forms.FileField):

                self.fields[field_name].widget.attrs.update({

                    'class': 'form-control',

                    'accept': '.pdf,.jpg,.jpeg,.png,image/*' if 'profile' in field_name else '.pdf,.jpg,.jpeg,.png'

                })

            elif isinstance(self.fields[field_name], forms.DateField):

                self.fields[field_name].widget.attrs.update({

                    'class': 'form-control',

                    'type': 'date'

                })

            elif isinstance(self.fields[field_name], forms.ChoiceField):

                self.fields[field_name].widget.attrs.update({'class': 'form-control'})

            elif isinstance(self.fields[field_name], forms.BooleanField):

                self.fields[field_name].widget.attrs.update({'class': 'form-check-input'})

            else:

                self.fields[field_name].widget.attrs.update({

                    'class': 'form-control',

                    'placeholder': self.fields[field_name].help_text or f'Enter {field_name.replace("_", " ")}'

                })



        # Add required attribute for HTML5 validation

        required_fields = [

            'username', 'first_name', 'last_name', 'email', 'confirm_email',

            'password1', 'password2'

        ]



        for field_name in required_fields:

            if field_name in self.fields:

                self.fields[field_name].widget.attrs['required'] = True



        # Add special attributes for phone number field

        if 'phone_number' in self.fields:

            self.fields['phone_number'].widget.attrs.update({

                'type': 'tel',

                'pattern': r'^[\d\s\-\+\(\)\.]+$',

                'placeholder': 'e.g., +63 912 345 6789',

                'title': 'Phone number can only contain numbers, spaces, dashes, plus signs, parentheses, and dots.'

            })



        # Specific placeholders

        self.fields['password1'].widget.attrs['placeholder'] = 'Create a strong password (8+ chars)'

        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm your password'

    

    def clean(self):

        cleaned_data = super().clean()

        passport_number = cleaned_data.get('passport_number')

        confirm_passport_number = cleaned_data.get('confirm_passport_number')

        passport_issue_date = cleaned_data.get('passport_issue_date')

        passport_expiry_date = cleaned_data.get('passport_expiry_date')

        date_of_birth = cleaned_data.get('date_of_birth')

        graduation_year = cleaned_data.get('graduation_year')



        # Phone number validation

        phone_number = cleaned_data.get('phone_number')

        if phone_number:

            import re

            # Remove any whitespace first

            phone_number = phone_number.strip()

            # Check if the phone number contains only allowed characters

            if not re.match(r'^[\d\s\-\+\(\)\.]+$', phone_number):

                raise ValidationError({

                    'phone_number': "Phone number can only contain numbers, spaces, dashes, plus signs, parentheses, and dots."

                })

            # Ensure there's at least one digit

            if not re.search(r'\d', phone_number):

                raise ValidationError({

                    'phone_number': "Phone number must contain at least one digit."

                })

            # Check minimum length (excluding formatting characters)

            digits_only = re.sub(r'[^\d]', '', phone_number)

            if len(digits_only) < 6:

                raise ValidationError({

                    'phone_number': "Phone number must contain at least 6 digits."

                })



        # Passport match

        if passport_number and confirm_passport_number and passport_number != confirm_passport_number:

            raise ValidationError("Passport numbers do not match.")



        # Email match

        email = cleaned_data.get('email')

        confirm_email = cleaned_data.get('confirm_email')

        if email and confirm_email and email != confirm_email:

            raise ValidationError("Email addresses do not match.")

        

        # Passport dates

        if passport_issue_date and passport_expiry_date:

            if passport_expiry_date <= passport_issue_date:

                raise ValidationError("Passport expiry date must be after issue date.")

            if passport_expiry_date < timezone.now().date():

                raise ValidationError("Passport must not be expired.")

        

        # DOB

        if date_of_birth and date_of_birth >= timezone.now().date():

            raise ValidationError("Date of birth must be in the past.")

        

        # Graduation year

        if graduation_year:

            current_year = timezone.now().year

            if graduation_year < 1900 or graduation_year > current_year:

                raise ValidationError("Graduation year must be between 1900 and current year.")

        

        # File validations

        document_fields = ['profile_image', 'passport_scan', 'tor', 'diploma', 'good_moral', 

                          'nbi_clearance', 'license_scan', 'nc2_tesda', 'academic_certificate']

        for field_name in document_fields:

            file_field = cleaned_data.get(field_name)

            if file_field:

                validate_file_size(file_field)

                valid_exts = ['.jpg', '.jpeg', '.png', '.gif'] if field_name == 'profile_image' else ['.pdf', '.jpg', '.jpeg', '.png']

                validate_file_extension(file_field, valid_exts)

        

        return cleaned_data

    

    def save(self, commit=True):

        user = super().save(commit=False)

        if commit:

            user.save()

            self.save_profile(user)

        return user

    

    def save_profile(self, user, commit=True):

        profile, created = Profile.objects.get_or_create(user=user)

        

        # Direct field mappings (form_field_name == model_field_name)

        profile_fields = [

            'middle_initial', 'country_of_birth', 'religion',

            'phone_number', 'date_of_birth', 'gender', 'nationality', 'address',

            'passport_number', 'passport_issue_date', 'passport_expiry_date', 'place_of_issue',

            'highest_education_level', 'graduation_year', 'year_graduated', 'field_of_study',

            'secondary_specialization',

            'preferred_country', 'willing_to_relocate', 'special_requirements',

            'profile_image', 'passport_scan', 'tor', 'diploma', 'good_moral',

            'nbi_clearance', 'license_scan', 'nc2_tesda', 'academic_certificate'

        ]

        for field in profile_fields:

            if field in self.cleaned_data:

                setattr(profile, field, self.cleaned_data[field])

        

        # Form field 'primary_specialization' maps to model field 'specialization'

        primary_spec = self.cleaned_data.get('primary_specialization')

        if primary_spec:

            profile.specialization = primary_spec

        

        university = self.cleaned_data.get('university')

        if university:

            profile.university = university.name if hasattr(university, 'name') else str(university)

        

        if commit:

            profile.save()

        return profile



