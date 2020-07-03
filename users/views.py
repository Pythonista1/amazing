from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from .forms import *
from django.http import HttpResponseForbidden
from dashboard.forms import *
from dashboard.models import *
from python_utils import *
from dashboard.views import *
from django.contrib.auth.views import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.core.paginator import Paginator,EmptyPage, PageNotAnInteger

class UserPasswordChangeView(LoginRequiredMixin, View):
    form_class = PasswordChangeForm
    template_name = 'users/home/change_password.html'

    def get(self, request):
        return render(request, self.template_name, {
            'form': self.form_class(request.user)
        })

    def post(self, request):
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, f'Password updated successfully.')
        return render(request, self.template_name, {'form': form})

def reset_user_password(request, user_pk):
    user = get_object_or_404(User, pk=user_pk)

    if not request.user.is_authenticated:
        return HttpResponseForbidden()

    password = password_generator()
    user.set_password(password)
    user.save()
    messages.success(request, "This user's password has been reset. Please notify the user of their new password.!")
    context = {'mod_user': user,
               'password': password}
    return render(request, 'users/home/reset_user_password.html', context)
@login_required
def view_profile(request):
    context={}
    member_id=request.user.full_name.id
    pledges=Pledges.objects.filter(Pledge_Made_By_id=member_id)
    tithes=Revenues.objects.filter(Revenue_filter='tithes',Member_Name_id=member_id)
    thanks=Revenues.objects.filter(Revenue_filter='thanks',Member_Name_id=member_id)
    context['thanks']=thanks
    context['pledges']=pledges
    context['tithes']=tithes
    context['member_id']=member_id
    return render(request, 'users/home/profile.html',context)
@login_required
def edit_profile(request):
    get_member = Members.objects.get(id=request.user.full_name.id)
    if request.method == 'POST':

        form = MembersForm(request.POST or None, request.FILES or None, instance=get_member)

        if form.is_valid():
            form.save()
            messages.success(request, f'Profile updated successfully.')
            return redirect('profile')

        else:
            form = MembersForm(instance=get_member)
            args = {'form': form}
            return render(request, 'users/home/update_profile.html', args)

    else:
        form = MembersForm(instance=get_member)
        args = {'form': form}
        return render(request, 'users/home/update_profile.html', args) 



@login_required
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        print(form.errors)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account has been created successfully!, User can now Login')
            return redirect('register')
    else:
        form=RegisterForm()
        users = User.objects.filter(full_name__is_active=True)
        count_users = users.count()
        context={ 'form':form, 'users':users, 'count_users':count_users}
        return render(request, 'users/home/register.html',context)


def MemberAccountRegister(request):
    members=Members.objects.all()
    if request.method == 'POST':
        form = MembershipAccountForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account has been created successfully!, You can now login')
            return redirect('login')
    else:
        form = MembershipAccountForm()
        return render(request, 'users/home/membershipaccount.html', {'form': form,'members':members})
@login_required
def delete_user(request,pk):
    user= get_object_or_404(User, id=pk)
    if request.method == "GET":
        user.delete()
        messages.success(request, "The User successfully deleted!")
        return redirect("register")
    context= {'user': user}
    return render(request, 'users/home/delete_user.html', context)
@login_required
def user_update(request, user_pk):
    user = get_object_or_404(User, pk=user_pk)
    if request.method == "POST":
        form = RegisterForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form = form.save()
            return redirect('register')
        else:
            form = RegisterForm(instance=user)
            args = {'form': form,}
            return render(request, 'users/home/user_update.html', args)
    else:
        form = RegisterForm(instance=user)
        args = {'form': form,}
        return render(request, 'users/home/user_update.html', args)
