import datetime
from functools import wraps
from django.core.exceptions import PermissionDenied
from django.utils.timezone import now, make_aware
from .models import Activity, Profile, CustomUser
from . import jalali

# --- CBV ---
class RoleRequiredMixin:
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied("ابتدا باید وارد شوید.")
        if str(request.user.user_type) not in self.allowed_roles:
            raise PermissionDenied("شما دسترسی لازم را ندارید.")
        return super().dispatch(request, *args, **kwargs)

# --- FBV ---
def role_required(allowed_roles=None):
    if allowed_roles is None:
        allowed_roles = []
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied("ابتدا باید وارد شوید.")
            if str(request.user.user_type) not in allowed_roles:
                raise PermissionDenied("شما دسترسی لازم را ندارید.")
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator

# --- CBV ---
class ApprovedProfileRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'user_profile') or request.user.user_profile.status != '2':
            raise PermissionDenied("پروفایل شما تایید نشده است.")
        return super().dispatch(request, *args, **kwargs)

# --- FBV ---
def approved_profile_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not hasattr(request.user, 'user_profile') or request.user.user_profile.status != '2':
            raise PermissionDenied("پروفایل شما تایید نشده است.")
        return view_func(request, *args, **kwargs)
    return _wrapped

# --- CBV ---
class DisApprovedProfileRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.user_profile.status != '3':
            raise PermissionDenied("پروفایل شما رد نشده است.")
        return super().dispatch(request, *args, **kwargs)

# --- FBV ---
def dis_approved_profile_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if request.user.user_profile.status != '3':
            raise PermissionDenied("پروفایل شما رد نشده است.")
        return view_func(request, *args, **kwargs)
    return _wrapped

# --- CBV ---
class EmployeeOwnerRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        employee = CustomUser.objects.get(pk=kwargs['pk'])
        if employee.manager != request.user:
            raise PermissionDenied("شما مدیر این کارمند نیستید.")
        return super().dispatch(request, *args, **kwargs)

# --- FBV ---
def employee_owner_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        employee = CustomUser.objects.get(pk=kwargs['pk'])
        if employee.manager != request.user:
            raise PermissionDenied("شما مدیر این کارمند نیستید.")
        return view_func(request, *args, **kwargs)
    return _wrapped

# --- CBV ---
class ActivityOwnerRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        activity = Activity.objects.get(pk=kwargs['pk'])
        if activity.user != request.user:
            raise PermissionDenied("شما صاحب این فعالیت نیستید.")
        return super().dispatch(request, *args, **kwargs)

# --- FBV ---
def activity_owner_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        activity = Activity.objects.get(pk=kwargs['pk'])
        if activity.user != request.user:
            raise PermissionDenied("شما صاحب این فعالیت نیستید.")
        return view_func(request, *args, **kwargs)
    return _wrapped

# --- CBV ---
class ManagerActivityRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        activity = Activity.objects.get(pk=kwargs['pk'])
        if activity.user.manager != request.user:
            raise PermissionDenied("این فعالیت مربوط به کارمند شما نیست.")
        return super().dispatch(request, *args, **kwargs)

# --- FBV ---
def manager_activity_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        activity = Activity.objects.get(pk=kwargs['pk'])
        if activity.user.manager != request.user:
            raise PermissionDenied("این فعالیت مربوط به کارمند شما نیست.")
        return view_func(request, *args, **kwargs)
    return _wrapped

# --- CBV ---
class VisibleActivityRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        activity = Activity.objects.get(pk=kwargs['pk'])
        if activity.visibility == False:
            raise PermissionDenied("این فعالیت مخفی است.")
        return super().dispatch(request, *args, **kwargs)

# --- FBV ---
def visible_activity_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        activity = Activity.objects.get(pk=kwargs['pk'])
        if activity.visibility == False:
            raise PermissionDenied("این فعالیت مخفی است.")
        return view_func(request, *args, **kwargs)
    return _wrapped

# --- CBV ---
class ProfileOwnerRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        profile = Profile.objects.get(pk=kwargs['pk'])
        if profile.user != request.user:
            raise PermissionDenied("این پروفایل متعلق به شما نیست.")
        return super().dispatch(request, *args, **kwargs)

# --- FBV ---
def profile_owner_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        profile = Profile.objects.get(pk=kwargs['pk'])
        if profile.user != request.user:
            raise PermissionDenied("این پروفایل متعلق به شما نیست.")
        return view_func(request, *args, **kwargs)
    return _wrapped

# --- CBV ---
class PassedUserApprovedProfileRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        user = CustomUser.objects.get(pk=kwargs['pk'])
        if not hasattr(user, 'user_profile') or user.user_profile.status != '2':
            raise PermissionDenied("این کارمند پروفایل تایید شده ندارد.")
        return super().dispatch(request, *args, **kwargs)

# --- FBV ---
def passed_user_approved_profile_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        user = CustomUser.objects.get(pk=kwargs['pk'])
        if not hasattr(user, 'user_profile') or user.user_profile.status != '2':
            raise PermissionDenied("این کارمند پروفایل تایید شده ندارد.")
        return view_func(request, *args, **kwargs)
    return _wrapped

# --- CBV ---
class ActiveTimeRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        activity = Activity.objects.get(pk=kwargs['pk'])

        # تبدیل تاریخ شمسی به میلادی
        start_date = jalali.Persian(activity.start_date).gregorian_datetime()
        end_date = jalali.Persian(activity.end_date).gregorian_datetime()

        # ساخت datetime
        start = datetime.datetime.combine(start_date, activity.start_time)
        end = datetime.datetime.combine(end_date, activity.end_time)

        # اطمینان از aware بودن
        if start.tzinfo is None:
            start = make_aware(start)
        if end.tzinfo is None:
            end = make_aware(end)

        if not (start <= now() <= end):
            raise PermissionDenied("این فعالیت در بازه زمانی معتبر نیست.")
        return super().dispatch(request, *args, **kwargs)

# --- FBV ---
def active_time_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        activity = Activity.objects.get(pk=kwargs['pk'])

        start_date = jalali.Persian(activity.start_date).gregorian_datetime()
        end_date = jalali.Persian(activity.end_date).gregorian_datetime()

        start = datetime.datetime.combine(start_date, activity.start_time)
        end = datetime.datetime.combine(end_date, activity.end_time)

        if start.tzinfo is None:
            start = make_aware(start)
        if end.tzinfo is None:
            end = make_aware(end)

        if not (start <= now() <= end):
            raise PermissionDenied("این فعالیت در بازه زمانی معتبر نیست.")
        return view_func(request, *args, **kwargs)
    return _wrapped
