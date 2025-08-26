from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

def validate_national_code(value):
    if len(value) != 10 or not value.isdigit():
        raise ValidationError('کد ملی باید ۱۰ رقم باشد.')

    check = int(value[9])
    s = sum(int(value[i]) * (10 - i) for i in range(9)) % 11

    if not ((s < 2 and check == s) or (s >= 2 and check == 11 - s)):
        raise ValidationError('کد ملی نامعتبر است.')

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('1', 'مدیر کل'),
        ('2', 'مدیر'),
        ('3', 'کارمند'),
    )

    user_type = models.CharField(verbose_name='سطح کاربر', max_length=10, choices=USER_TYPE_CHOICES, default='1')

    manager = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='manager_employees',
        limit_choices_to={'user_type': '2'},
        verbose_name='مدیر'
    )

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'
    
    def __str__(self):
        return f'{self.get_user_type_display()}: {self.get_full_name()}'

class Profile(models.Model):
    STATUS_CHOICES = (
        ('1', 'در انتظار بررسی'),
        ('2', 'تایید شده'),
        ('3', 'رد شده'),
    )

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='user_profile', verbose_name='کاربر', editable=False)
    phone_number = models.CharField(
        verbose_name='تلفن همراه',
        max_length=11,
        unique=True,
        help_text='09123456789',
        validators=[RegexValidator(r'^\d{11}$', message='شماره تلفن همراه باید 11 رقمی و با 0 اول باشد.')]
    )
    address = models.CharField(verbose_name='آدرس', max_length=700)
    phone_number_1 = models.CharField(
        verbose_name='تلفن همراه بستگان',
        max_length=11,
        help_text='09123456789',
        validators=[RegexValidator(r'^\d{11}$', message='شماره تلفن همراه باید 11 رقمی و با 0 اول باشد.')]
    )
    phone_number_2 = models.CharField(
        verbose_name='تلفن همراه بستگان',
        max_length=11,
        help_text='09123456789',
        validators=[RegexValidator(r'^\d{11}$', message='شماره تلفن همراه باید 11 رقمی و با 0 اول باشد.')]
    )
    national_code = models.CharField(verbose_name='کد ملی', max_length=10, unique=True, validators=[validate_national_code])
    birthdate = models.CharField(verbose_name='تاریخ تولد', max_length=10)
    national_card = models.ImageField(verbose_name='تصویر کارت ملی', upload_to='national_card/')
    guarantee = models.ImageField(verbose_name='تصویر ضمانت نامه', upload_to='guarantee/', null=True, blank=True)
    status = models.CharField(verbose_name='وضعیت', max_length=20, choices=STATUS_CHOICES, default='1')

    class Meta:
        verbose_name = 'پروفایل'
        verbose_name_plural = 'پروفایل ها'
    
    def __str__(self):
        return f'پروفایل {self.user} با وضعیت {self.get_status_display()}'

class Conversation(models.Model):
    users = models.ManyToManyField(CustomUser, related_name='users_conversations', verbose_name='کاربران تیکت')

    class Meta:
        verbose_name = 'تیکت'
        verbose_name_plural = 'تیکت ها'

class Message(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_messages', verbose_name='کاربر', editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='conversation_messages', verbose_name='تیکت', editable=False)
    body = models.TextField(verbose_name='پیام')
    created_at = models.DateTimeField(verbose_name='تاریخ', auto_now=True)
    seen = models.BooleanField(verbose_name='دیده شده', default=False)

    class Meta:
        verbose_name = 'پیام'
        verbose_name_plural = 'پیام ها'

class Activity(models.Model):
    SENSITIVITY_CHOICES = (
        ('1', 'کم'),
        ('2', 'متوسط'),
        ('3', 'زیاد'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_activities', verbose_name='کاربر', editable=False)
    creater = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='creater_activities', verbose_name='خالق', editable=False)
    title = models.CharField(verbose_name='عنوان', max_length=1000)
    body = models.TextField(verbose_name='توضیحات')
    start_date = models.CharField(verbose_name='تاریخ شروع', max_length=10)
    start_time = models.TimeField(verbose_name='ساعت شروع')
    end_date = models.CharField(verbose_name='تاریخ پایان', max_length=10)
    end_time = models.TimeField(verbose_name='ساعت پایان')
    sensitivity = models.CharField(verbose_name='حساسیت', max_length=5, choices=SENSITIVITY_CHOICES)
    is_completed = models.BooleanField(verbose_name='وضعیت انجام', default=False)
    visibility = models.BooleanField(verbose_name='وضعیت نمایش')

    class Meta:
        verbose_name = 'فعالیت'
        verbose_name_plural = 'فعالیت ها'

    def __str__(self):
        return self.title