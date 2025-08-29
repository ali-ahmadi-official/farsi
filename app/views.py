from collections import defaultdict
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView, View
from django.http import HttpResponseForbidden
from django.db.models import Q
from . import models, forms, mixins, jalali, extras

def custom_context(request):
    if request.user.is_authenticated:
        not_seen_messages = models.Message.objects.filter(conversation__users=request.user, seen=False).exclude(user=request.user)

        return {
            'not_seen_messages_count': not_seen_messages.count(),
        }
    else:
        return {
            'not_login': True,
        }

def main(request):
    return redirect('login')

def login(request):
    form = forms.LoginForm()

    if request.method == 'POST':
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                auth_login(request, user)

                if getattr(user, 'user_type', '1') == '1':
                    return redirect('super_admin_dashboard')
                elif getattr(user, 'user_type', '2') == '2':
                    return redirect('manager_dashboard')
                else:
                    return redirect('employee_dashboard')
            else:
                messages.error(request, 'نام کاربری یا رمز عبور اشتباه است.')

    return render(request, 'login.html', {'form': form})

# region super admin views

@login_required
@mixins.role_required(['1'])
def super_admin_dashboard(request):
    users = models.CustomUser.objects.all().order_by('-id')
    activities = models.Activity.objects.all().order_by('-id')
    profiles_awaiting = models.Profile.objects.filter(status='1').order_by('-id')

    context = {
        'users_count': users.count(),
        'managers_count': users.filter(user_type='2').count(),
        'employees_count': users.filter(user_type='3').count(),
        'activities_count': activities.filter(visibility=True).count(),
        'profiles': profiles_awaiting,
        'activities': activities.filter(visibility=False),
    }

    return render(request, 'super_admin/dashboard.html', context)

class SuperAdminUserListView(LoginRequiredMixin, mixins.RoleRequiredMixin, ListView):
    allowed_roles = ['1']
    model = models.CustomUser
    template_name = 'super_admin/users.html'
    context_object_name = 'users'
    paginate_by = 100
    ordering = '-id'

    def get_queryset(self):
        queryset = super().get_queryset()
        search_full_name = self.request.GET.get('search_full_name')
        search_user_name = self.request.GET.get('search_user_name')
        user_type = self.request.GET.get('user_type')

        if search_full_name:
            queryset = queryset.filter(
                Q(first_name__icontains=search_full_name) | 
                Q(last_name__icontains=search_full_name)
            )
        if search_user_name:
            queryset = queryset.filter(
                Q(username__icontains=search_user_name)
            )
        if user_type:
            queryset = queryset.filter(user_type=user_type)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_type'] = self.request.GET.get('user_type', '')
        return context

class SuperAdminUserCreateView(LoginRequiredMixin, mixins.RoleRequiredMixin, CreateView):
    allowed_roles = ['1']
    form_class = forms.CustomUserCreationForm
    template_name = 'super_admin/add_user.html'
    
    def get_success_url(self):
        user = self.object

        if user.user_type == '3':
            return reverse('super_admin_select_manager', kwargs={'pk': self.object.id})
        else:
            return reverse('super_admin_users')

class SuperAdminSelectManagerView(LoginRequiredMixin, mixins.RoleRequiredMixin, UpdateView):
    allowed_roles = ['1']
    model = models.CustomUser
    form_class = forms.SelectManagerForm
    template_name = 'super_admin/select_manager.html'

    def get_success_url(self):
        return reverse('super_admin_users')

class SuperAdminUserDetailView(LoginRequiredMixin, mixins.RoleRequiredMixin, DetailView):
    allowed_roles = ['1']
    model = models.CustomUser
    template_name = 'super_admin/user.html'
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        context['activities'] = user.user_activities.filter(visibility=True).order_by('-id')
        return context

class SuperAdminUserUpdateView(LoginRequiredMixin, mixins.RoleRequiredMixin, UpdateView):
    allowed_roles = ['1']
    model = models.CustomUser
    form_class = forms.CustomUserUpdateForm
    template_name = 'super_admin/edit_user.html'

    def get_success_url(self):
        return reverse('super_admin_users')

class SuperAdminUserDeleteView(DeleteView):
    model = models.CustomUser
    template_name = 'super_admin/confirm_delete.html'
    success_url = reverse_lazy('super_admin_users')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['previous_url'] = self.request.META.get('HTTP_REFERER', '/')
        return context

class SuperAdminProfileListView(LoginRequiredMixin, mixins.RoleRequiredMixin, ListView):
    allowed_roles = ['1']
    model = models.Profile
    template_name = 'super_admin/profiles.html'
    paginate_by = 100
    context_object_name = 'profiles'
    ordering = '-id'

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get('status')

        if status:
            queryset = queryset.filter(status=status)

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status'] = self.request.GET.get('status', '')
        return context

class SuperAdminProfileDetailView(LoginRequiredMixin, mixins.RoleRequiredMixin, DetailView):
    allowed_roles = ['1']
    model = models.Profile
    template_name = 'super_admin/profile.html'

class SuperAdminProfileUpdateView(LoginRequiredMixin, mixins.RoleRequiredMixin, UpdateView):
    allowed_roles = ['1']
    model = models.Profile
    form_class = forms.ProfileUpdateForm
    template_name = 'super_admin/edit_profile.html'
    
    def get_success_url(self):
        return reverse('super_admin_profile', kwargs={'pk': self.object.id})

class SuperAdminActivityListView(LoginRequiredMixin, mixins.RoleRequiredMixin, ListView):
    allowed_roles = ['1']
    model = models.Activity
    template_name = 'super_admin/activities.html'
    context_object_name = 'activities'
    paginate_by = 100
    ordering = '-id'

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q')
        is_completed = self.request.GET.get('is_completed')
        visibility = self.request.GET.get('visibility')

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query)
            )
        if is_completed:
            queryset = queryset.filter(is_completed=is_completed)
        if visibility:
            queryset = queryset.filter(visibility=visibility)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_completed'] = self.request.GET.get('is_completed', '')
        context['visibility'] = self.request.GET.get('visibility', '')
        return context

@login_required
@mixins.role_required(['1'])
def super_admin_create_bulk_activity(request):
    if request.method == 'POST':
        form = forms.SuperAdminBulkActivityForm(request.POST)
        if form.is_valid():
            users = form.cleaned_data['users']
            activity_data = {
                'creater': request.user,
                'title': form.cleaned_data['title'],
                'body': form.cleaned_data['body'],
                'start_date': form.cleaned_data['start_date'],
                'start_time': form.cleaned_data['start_time'],
                'end_date': form.cleaned_data['end_date'],
                'end_time': form.cleaned_data['end_time'],
                'sensitivity': form.cleaned_data['sensitivity'],
                'visibility': True,
            }
            for user in users:
                models.Activity.objects.create(user=user, **activity_data)
            return redirect('super_admin_activities')
    else:
        form = forms.SuperAdminBulkActivityForm()
    return render(request, 'super_admin/add_activity.html', {'form': form})

class SuperAdminActivityDetailView(LoginRequiredMixin, mixins.RoleRequiredMixin, DetailView):
    allowed_roles = ['1']
    model = models.Activity
    template_name = 'super_admin/activity.html'
    context_object_name = 'activity'

class SuperAdminActivityUpdateView(LoginRequiredMixin, mixins.RoleRequiredMixin, UpdateView):
    allowed_roles = ['1']
    model = models.Activity
    form_class = forms.ActivityUpdateForm
    template_name = 'super_admin/edit_activity.html'

    def get_success_url(self):
        return reverse('super_admin_activity', kwargs={'pk': self.object.id})

class SuperAdminActivityDeleteView(LoginRequiredMixin, mixins.RoleRequiredMixin, DeleteView):
    allowed_roles = ['1']
    model = models.Activity
    template_name = 'super_admin/confirm_delete.html'
    success_url = reverse_lazy('super_admin_activities')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['previous_url'] = self.request.META.get('HTTP_REFERER', '/')
        return context

class SuperAdminTicketListView(LoginRequiredMixin, mixins.RoleRequiredMixin, ListView):
    allowed_roles = ['1']
    model = models.Conversation
    template_name = 'super_admin/tickets.html'
    context_object_name = 'tickets'
    paginate_by = 100
    ordering = ['-id']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user

        unseen_counts = {}

        for conversation in context['tickets']:
            unseen_count = conversation.conversation_messages.filter(
                seen=False
            ).exclude(user=current_user).count()

            unseen_counts[conversation.id] = unseen_count

        context['unseen_counts'] = unseen_counts
        return context

class SuperAdminTicketCreateOrRedirectView(LoginRequiredMixin, mixins.RoleRequiredMixin, View):
    allowed_roles = ['1']
    form_class = forms.SuperAdminTicketCreateForm
    template_name = 'super_admin/add_ticket.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(user=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, user=request.user)
        if form.is_valid():
            selected_user = form.cleaned_data['user']
            current_user = request.user

            conversations = models.Conversation.objects.filter(users=current_user).filter(users=selected_user)
            conversation = None
            for conv in conversations:
                if conv.users.count() == 2:
                    conversation = conv
                    break

            if conversation:
                return redirect('chat', pk=conversation.pk)
            else:
                conversation = models.Conversation.objects.create()
                conversation.users.add(current_user, selected_user)
                return redirect('chat', pk=conversation.pk)

        return render(request, self.template_name, {'form': form})

# endregion

# region manager views

@login_required
@mixins.role_required(['2'])
def manager_dashboard(request):
    user = request.user
    employees = models.CustomUser.objects.filter(
        manager=user,
        user_type='3',
        user_profile__status='2'
    ).order_by('-id')

    some_employees = employees[:3]
    some_activities = models.Activity.objects.filter(user__in=employees, visibility=True).order_by('-id')[:3]
    some_my_activities = models.Activity.objects.filter(user=user, visibility=True).order_by('-id')[:3]
    hidden_activities_count = models.Activity.objects.filter(creater=user, visibility=False).count()

    context = {
        'users': some_employees,
        'my_activities': some_my_activities,
        'activities': some_activities,
        'hidden_activities_count': hidden_activities_count,
    }

    return render(request, 'manager/dashboard.html', context)

class ManagerUserListView(LoginRequiredMixin, mixins.RoleRequiredMixin, ListView):
    allowed_roles = ['2']
    model = models.CustomUser
    template_name = 'manager/users.html'
    context_object_name = 'users'
    paginate_by = 100
    ordering = '-id'

    def get_queryset(self):
        queryset = super().get_queryset().filter(manager=self.request.user, user_type='3', user_profile__status='2')
        search_full_name = self.request.GET.get('search_full_name')

        if search_full_name:
            queryset = queryset.filter(
                Q(first_name__icontains=search_full_name) | 
                Q(last_name__icontains=search_full_name)
            )

        return queryset

class ManagerUserDetailView(LoginRequiredMixin, mixins.RoleRequiredMixin, mixins.EmployeeOwnerRequiredMixin, mixins.PassedUserApprovedProfileRequiredMixin, DetailView):
    allowed_roles = ['2']
    model = models.CustomUser
    template_name = 'manager/user.html'
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        context['activities'] = user.user_activities.filter(visibility=True).order_by('-id')
        return context

class ManagerMyActivityListView(LoginRequiredMixin, mixins.RoleRequiredMixin, ListView):
    allowed_roles = ['2']
    model = models.Activity
    template_name = 'manager/my_activities.html'
    context_object_name = 'my_activities'
    paginate_by = 100
    ordering = '-id'

    def get_queryset(self):
        queryset = super().get_queryset().filter(visibility=True, user=self.request.user)
        search_query = self.request.GET.get('q')
        is_completed = self.request.GET.get('is_completed')

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query)
            )
        if is_completed:
            queryset = queryset.filter(is_completed=is_completed)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_completed'] = self.request.GET.get('is_completed', '')
        return context

class ManagerMyActivityDetailView(LoginRequiredMixin, mixins.RoleRequiredMixin, mixins.ActivityOwnerRequiredMixin, mixins.VisibleActivityRequiredMixin, DetailView):
    allowed_roles = ['2']
    model = models.Activity
    template_name = 'manager/activity.html'
    context_object_name = 'activity'

class ManagerMyActivityUpdateView(LoginRequiredMixin, mixins.RoleRequiredMixin, mixins.ActivityOwnerRequiredMixin, mixins.VisibleActivityRequiredMixin, mixins.ActiveTimeRequiredMixin, UpdateView):
    allowed_roles = ['2']
    model = models.Activity
    fields = ['is_completed']
    template_name = 'manager/is_completed_activity.html'
    success_url = reverse_lazy('manager_my_activities')

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.is_completed = True
        obj.save()
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['previous_url'] = self.request.META.get('HTTP_REFERER', '/')
        return context

class ManagerActivityListView(LoginRequiredMixin, mixins.RoleRequiredMixin, ListView):
    allowed_roles = ['2']
    model = models.Activity
    template_name = 'manager/activities.html'
    context_object_name = 'activities'
    paginate_by = 100
    ordering = '-id'

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            visibility=True,
            user__manager=self.request.user,
            user__user_type='3',
            user__user_profile__status='2'
        )
        search_query = self.request.GET.get('q')
        is_completed = self.request.GET.get('is_completed')

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query)
            )
        if is_completed:
            queryset = queryset.filter(is_completed=is_completed)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        hidden_activities_count = models.Activity.objects.filter(creater=user, visibility=False).count()

        context['is_completed'] = self.request.GET.get('is_completed', '')
        context['hidden_activities_count'] = hidden_activities_count

        return context

@login_required
@mixins.role_required(['2'])
def manager_create_bulk_activity(request):
    if request.method == 'POST':
        form = forms.ManagerBulkActivityForm(request.POST, user=request.user)
        if form.is_valid():
            users = form.cleaned_data['users']
            activity_data = {
                'creater': request.user,
                'title': form.cleaned_data['title'],
                'body': form.cleaned_data['body'],
                'start_date': form.cleaned_data['start_date'],
                'start_time': form.cleaned_data['start_time'],
                'end_date': form.cleaned_data['end_date'],
                'end_time': form.cleaned_data['end_time'],
                'sensitivity': form.cleaned_data['sensitivity'],
                'visibility': False,
            }
            for user in users:
                models.Activity.objects.create(user=user, **activity_data)
            return redirect('manager_activities')
    else:
        form = forms.ManagerBulkActivityForm(user=request.user)
    return render(request, 'manager/add_activity.html', {'form': form})

class ManagerActivityDetailView(LoginRequiredMixin, mixins.RoleRequiredMixin, mixins.ManagerActivityRequiredMixin, DetailView):
    allowed_roles = ['2']
    model = models.Activity
    template_name = 'manager/activity.html'
    context_object_name = 'activity'

class ManagerTicketListView(LoginRequiredMixin, mixins.RoleRequiredMixin, ListView):
    allowed_roles = ['2']
    model = models.Conversation
    template_name = 'manager/tickets.html'
    context_object_name = 'tickets'
    paginate_by = 100
    ordering = '-id'

    def get_queryset(self):
        return super().get_queryset().filter(users=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        current_user = self.request.user

        unseen_counts = {}

        for conversation in context['tickets']:
            unseen_count = conversation.conversation_messages.filter(
                seen=False
            ).exclude(user=current_user).count()

            unseen_counts[conversation.id] = unseen_count

        context['unseen_counts'] = unseen_counts
        return context

class ManagerTicketCreateOrRedirectView(LoginRequiredMixin, mixins.RoleRequiredMixin, View):
    allowed_roles = ['2']
    form_class = forms.ManagerTicketCreateForm
    template_name = 'manager/add_ticket.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(user=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, user=request.user)
        if form.is_valid():
            selected_user = form.cleaned_data['user']
            current_user = request.user

            conversations = models.Conversation.objects.filter(users=current_user).filter(users=selected_user)
            conversation = None
            for conv in conversations:
                if conv.users.count() == 2:
                    conversation = conv
                    break

            if conversation:
                return redirect('chat', pk=conversation.pk)
            else:
                conversation = models.Conversation.objects.create()
                conversation.users.add(current_user, selected_user)
                return redirect('chat', pk=conversation.pk)

        return render(request, self.template_name, {'form': form})

# endregion

# region employee views

@login_required
@mixins.role_required(['3'])
def employee_dashboard(request):
    some_activities = models.Activity.objects.filter(visibility=True, user=request.user).order_by('-id')[:3]

    context = {
        'activities': some_activities,
    }

    return render(request, 'employee/dashboard.html', context)

class EmployeeProfileCreateView(LoginRequiredMixin, mixins.RoleRequiredMixin, CreateView):
    allowed_roles = ['3']
    model = models.Profile
    form_class = forms.ProfileEmployeeForm
    template_name = 'employee/add_profile.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('employee_profile', kwargs={'pk': self.object.id})

class EmployeeProfileDetailView(LoginRequiredMixin, mixins.RoleRequiredMixin, mixins.ProfileOwnerRequiredMixin, DetailView):
    allowed_roles = ['3']
    model = models.Profile
    template_name = 'employee/profile.html'

class EmployeeProfileUpdateView(LoginRequiredMixin, mixins.RoleRequiredMixin, mixins.ProfileOwnerRequiredMixin, mixins.DisApprovedProfileRequiredMixin, UpdateView):
    allowed_roles = ['3']
    model = models.Profile
    form_class = forms.ProfileEmployeeForm
    template_name = 'employee/edit_profile.html'

    def get_success_url(self):
        return reverse('employee_profile', kwargs={'pk': self.object.id})

class EmployeeActivityListView(LoginRequiredMixin, mixins.RoleRequiredMixin, mixins.ApprovedProfileRequiredMixin, ListView):
    allowed_roles = ['3']
    model = models.Activity
    template_name = 'employee/activities.html'
    context_object_name = 'activities'
    paginate_by = 100
    ordering = '-id'

    def get_queryset(self):
        queryset = super().get_queryset().filter(visibility=True, user=self.request.user)
        search_query = self.request.GET.get('q')
        is_completed = self.request.GET.get('is_completed')

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query)
            )
        if is_completed:
            queryset = queryset.filter(is_completed=is_completed)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_completed'] = self.request.GET.get('is_completed', '')
        return context

class EmployeeActivityDetailView(LoginRequiredMixin, mixins.RoleRequiredMixin, mixins.ActivityOwnerRequiredMixin, mixins.VisibleActivityRequiredMixin, mixins.ApprovedProfileRequiredMixin, DetailView):
    allowed_roles = ['3']
    model = models.Activity
    template_name = 'employee/activity.html'
    context_object_name = 'activity'

class EmployeeActivityUpdateView(LoginRequiredMixin, mixins.RoleRequiredMixin, mixins.ActivityOwnerRequiredMixin, mixins.VisibleActivityRequiredMixin, mixins.ApprovedProfileRequiredMixin, mixins.ActiveTimeRequiredMixin, UpdateView):
    allowed_roles = ['3']
    model = models.Activity
    fields = ['is_completed']
    template_name = 'employee/is_completed_activity.html'
    success_url = reverse_lazy('employee_activities')

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.is_completed = True
        obj.save()
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['previous_url'] = self.request.META.get('HTTP_REFERER', '/')
        return context

class EmployeeTicketListView(LoginRequiredMixin, mixins.RoleRequiredMixin, ListView):
    allowed_roles = ['3']
    model = models.Conversation
    template_name = 'employee/tickets.html'
    context_object_name = 'tickets'
    paginate_by = 100
    ordering = '-id'

    def get_queryset(self):
        return super().get_queryset().filter(users=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        current_user = self.request.user

        unseen_counts = {}

        for conversation in context['tickets']:
            unseen_count = conversation.conversation_messages.filter(
                seen=False
            ).exclude(user=current_user).count()

            unseen_counts[conversation.id] = unseen_count

        context['unseen_counts'] = unseen_counts
        return context

class EmployeeTicketCreateOrRedirectView(LoginRequiredMixin, mixins.RoleRequiredMixin, View):
    allowed_roles = ['3']
    form_class = forms.EmployeeTicketCreateForm
    template_name = 'employee/add_ticket.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(user=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, user=request.user)
        if form.is_valid():
            selected_user = form.cleaned_data['user']
            current_user = request.user

            conversations = models.Conversation.objects.filter(users=current_user).filter(users=selected_user)
            conversation = None
            for conv in conversations:
                if conv.users.count() == 2:
                    conversation = conv
                    break

            if conversation:
                return redirect('chat', pk=conversation.pk)
            else:
                conversation = models.Conversation.objects.create()
                conversation.users.add(current_user, selected_user)
                return redirect('chat', pk=conversation.pk)

        return render(request, self.template_name, {'form': form})

# endregion

@login_required
@mixins.user_in_conversation_or_admin
def chat(request, pk):
    user = request.user
    conversation = models.Conversation.objects.get(pk=pk)
    all_messages = models.Message.objects.filter(conversation=conversation).order_by('-created_at')
    messages = all_messages[:50]
    messages = reversed(messages)

    you_messages_not_seen = all_messages.exclude(user=user).filter(seen=False)
    for you_message_not_seen in you_messages_not_seen:
        you_message_not_seen.seen = True
        you_message_not_seen.save()

    grouped_messages = defaultdict(list)
    for message in messages:
        msg_date = message.created_at.date()
        grouped_messages[msg_date].append(message)

    messages_by_day = []
    for day, msgs in grouped_messages.items():
        y, m, d = jalali.Gregorian(day).persian_tuple()
        persian_date = f"{d} {extras.PERSIAN_MONTHS[m]} {y}"
        messages_by_day.append({
            "date": persian_date,
            "messages": msgs
        })

    context = {
        "user": user,
        "conversation": conversation,
        "messages_by_day": messages_by_day
    }
    return render(request, 'chat/chat.html', context)

@login_required
@mixins.user_in_conversation_or_admin
def update_chat(request, pk):
    user = request.user
    after_id = request.GET.get("after_id")
    conversation = get_object_or_404(models.Conversation, pk=pk)

    messages = models.Message.objects.filter(
        conversation=conversation, id__gt=after_id
    ).order_by("created_at")

    context = {
        'user': user,
        'conversation': conversation,
        'messages': messages,
    }

    return render(request, "chat/messages.html", context)

@login_required
@mixins.user_in_conversation_or_admin
def load_older_messages(request, pk):
    before_id = request.GET.get("before_id")
    conversation = get_object_or_404(models.Conversation, pk=pk)

    messages = models.Message.objects.filter(
        conversation=conversation, id__lt=before_id
    ).order_by('-created_at')[:50]
    messages = reversed(messages)

    context = {
        'user': request.user,
        'conversation': conversation,
        'messages': messages,
    }

    has_more = models.Message.objects.filter(conversation=conversation, id__lt=before_id).exists()

    return render(request, "chat/load_older.html", context | {"has_more": has_more})

@login_required
@mixins.user_in_conversation_or_admin
def add_chat(request, pk):
    user = request.user
    conversation = get_object_or_404(models.Conversation, pk=pk)

    if request.method == 'POST':
        form = forms.ChatCreateForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.user = user
            message.conversation = conversation
            message.save()
    return redirect('chat', pk=conversation.pk)

@login_required
@mixins.user_is_message_owner_or_admin
def edit_chat(request, pk):
    message = get_object_or_404(models.Message, pk=pk)

    if request.method == 'POST':
        form = forms.ChatUpdateForm(request.POST, request.FILES, instance=message)
        if form.is_valid():
            form.save()
    return redirect('chat', pk=message.conversation.pk)

@login_required
@mixins.user_is_message_owner_or_admin
def delete_chat(request, pk):
    message = get_object_or_404(models.Message, pk=pk)

    if request.method == 'POST':
        conversation_pk = message.conversation.pk
        message.delete()
        return redirect('chat', pk=conversation_pk)