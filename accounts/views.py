from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import CustomUser, Department, Grade, JobTitle
from leaves.models import LeaveApplication, LeaveBalance
import random
import string


def generate_temp_password(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.role == role or user.secondary_role == role:
                login(request, user)
                request.session['active_role'] = role
                return redirect('dashboard')
            else:
                messages.error(request, 'Selected role does not match your account.')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    user = request.user
    active_role = request.session.get('active_role', user.role)

    if active_role == 'it_admin':
        total_users = CustomUser.objects.exclude(id=user.id).count()
        total_departments = Department.objects.count()
        total_grades = Grade.objects.count()
        return render(request, 'accounts/dashboard_admin.html', {
            'total_users': total_users,
            'total_departments': total_departments,
            'total_grades': total_grades,
        })

    elif active_role == 'employee':
        leave_balances = LeaveBalance.objects.filter(user=user)
        supervisor_requests = None
        if user.is_supervisor:
            supervisor_requests = LeaveApplication.objects.filter(
                status='pending',
                chosen_supervisor=user
            ).order_by('-applied_at')
        return render(request, 'accounts/dashboard_employee.html', {
            'leave_balances': leave_balances,
            'supervisor_requests': supervisor_requests,
        })

    elif active_role == 'hr':
        recent_applications = LeaveApplication.objects.all().order_by('-applied_at')[:10]
        pending_count = LeaveApplication.objects.filter(
            status='supervisor_approved'
        ).count()
        return render(request, 'accounts/dashboard_hr.html', {
            'recent_applications': recent_applications,
            'pending_count': pending_count,
        })

    elif active_role == 'approver':
        supervisor_pending = LeaveApplication.objects.filter(
            status='pending',
            chosen_supervisor=user
        ).order_by('-applied_at')
        approver_pending = LeaveApplication.objects.filter(
            status='forwarded_to_approver',
            chosen_approver=user
        ).order_by('-applied_at')
        return render(request, 'accounts/dashboard_approver.html', {
            'supervisor_pending': supervisor_pending,
            'pending_applications': approver_pending,
        })

    else:
        request.session['active_role'] = user.role
        return redirect('dashboard')


@login_required
def manage_users(request):
    active_role = request.session.get('active_role', request.user.role)
    if active_role != 'it_admin':
        return redirect('dashboard')
    users = CustomUser.objects.all().exclude(id=request.user.id).order_by('first_name', 'last_name')
    return render(request, 'accounts/manage_users.html', {'users': users})


@login_required
def create_user(request):
    active_role = request.session.get('active_role', request.user.role)
    if active_role != 'it_admin':
        return redirect('dashboard')

    departments = Department.objects.all().order_by('name')
    grades = Grade.objects.all()
    job_titles = JobTitle.objects.all().order_by('name')

    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        secondary_role = request.POST.get('secondary_role')
        grade_id = request.POST.get('grade')
        job_title_id = request.POST.get('job_title')
        department_id = request.POST.get('department')
        phone = request.POST.get('phone')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        else:
            user = CustomUser.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                role=role,
                phone=phone,
                temp_password=password,
            )
            if secondary_role:
                user.secondary_role = secondary_role
            if department_id:
                user.department = Department.objects.get(id=department_id)
            if grade_id:
                user.grade = Grade.objects.get(id=grade_id)
            if job_title_id:
                user.job_title = JobTitle.objects.get(id=job_title_id)
            user.is_supervisor = True if request.POST.get('is_supervisor') else False
            user.save()
            messages.success(request, f'Account for {first_name} {last_name} created successfully!')
            return redirect('manage_users')

    return render(request, 'accounts/create_user.html', {
        'departments': departments,
        'grades': grades,
        'job_titles': job_titles,
    })


@login_required
def edit_user(request, user_id):
    active_role = request.session.get('active_role', request.user.role)
    if active_role != 'it_admin':
        return redirect('dashboard')

    target_user = get_object_or_404(CustomUser, id=user_id)
    departments = Department.objects.all()
    grades = Grade.objects.all()
    job_titles = JobTitle.objects.all()

    if request.method == 'POST':
        target_user.first_name = request.POST.get('first_name')
        target_user.last_name = request.POST.get('last_name')
        target_user.email = request.POST.get('email')
        target_user.role = request.POST.get('role')
        target_user.phone = request.POST.get('phone')
        secondary_role = request.POST.get('secondary_role')
        target_user.secondary_role = secondary_role if secondary_role else None
        target_user.is_supervisor = True if request.POST.get('is_supervisor') else False

        grade_id = request.POST.get('grade')
        job_title_id = request.POST.get('job_title')
        department_id = request.POST.get('department')

        target_user.department = Department.objects.get(id=department_id) if department_id else None
        target_user.grade = Grade.objects.get(id=grade_id) if grade_id else None
        target_user.job_title = JobTitle.objects.get(id=job_title_id) if job_title_id else None
        target_user.save()

        messages.success(request, f'User {target_user.get_full_name()} updated successfully!')
        return redirect('manage_users')

    return render(request, 'accounts/edit_user.html', {
        'target_user': target_user,
        'departments': departments,
        'grades': grades,
        'job_titles': job_titles,
    })


@login_required
def reset_password(request, user_id):
    active_role = request.session.get('active_role', request.user.role)
    if active_role != 'it_admin':
        return redirect('dashboard')

    target_user = get_object_or_404(CustomUser, id=user_id)

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        target_user.set_password(new_password)
        target_user.temp_password = new_password
        target_user.save()
        messages.success(request, f'Password for {target_user.get_full_name()} reset successfully!')
        return redirect('manage_users')

    return render(request, 'accounts/reset_password.html', {
        'target_user': target_user,
    })


@login_required
def manage_departments(request):
    active_role = request.session.get('active_role', request.user.role)
    if active_role != 'it_admin':
        return redirect('dashboard')

    departments = Department.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        if name:
            if Department.objects.filter(name__iexact=name.strip()).exists():
                messages.error(request, f'A department named "{name}" already exists.')
            else:
                Department.objects.create(name=name.strip(), description=description)
                messages.success(request, f'Department "{name}" created successfully!')
                return redirect('manage_departments')

    return render(request, 'accounts/manage_departments.html', {
        'departments': departments,
    })


@login_required
def edit_department(request, dept_id):
    active_role = request.session.get('active_role', request.user.role)
    if active_role != 'it_admin':
        return redirect('dashboard')

    department = get_object_or_404(Department, id=dept_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        if name:
            if Department.objects.filter(name__iexact=name.strip()).exclude(id=department.id).exists():
                messages.error(request, f'A department named "{name}" already exists.')
            else:
                department.name = name.strip()
                department.description = description
                department.save()
                messages.success(request, f'Department "{name}" updated successfully!')
                return redirect('manage_departments')

    return render(request, 'accounts/edit_department.html', {
        'department': department,
    })


@login_required
def delete_department(request, dept_id):
    active_role = request.session.get('active_role', request.user.role)
    if active_role != 'it_admin':
        return redirect('dashboard')
    department = get_object_or_404(Department, id=dept_id)
    department.delete()
    messages.success(request, 'Department deleted successfully!')
    return redirect('manage_departments')


@login_required
def manage_grades(request):
    active_role = request.session.get('active_role', request.user.role)
    if active_role != 'it_admin':
        return redirect('dashboard')

    grades = Grade.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        if name:
            if Grade.objects.filter(name__iexact=name.strip()).exists():
                messages.error(request, f'A grade named "{name}" already exists.')
            else:
                Grade.objects.create(name=name.strip(), description=description)
                messages.success(request, f'Grade "{name}" created successfully!')
                return redirect('manage_grades')

    return render(request, 'accounts/manage_grades.html', {
        'grades': grades,
    })


@login_required
def edit_grade(request, grade_id):
    active_role = request.session.get('active_role', request.user.role)
    if active_role != 'it_admin':
        return redirect('dashboard')

    grade = get_object_or_404(Grade, id=grade_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        if name:
            if Grade.objects.filter(name__iexact=name.strip()).exclude(id=grade.id).exists():
                messages.error(request, f'A grade named "{name}" already exists.')
            else:
                grade.name = name.strip()
                grade.description = description
                grade.save()
                messages.success(request, f'Grade "{name}" updated successfully!')
                return redirect('manage_grades')

    return render(request, 'accounts/edit_grade.html', {
        'grade': grade,
    })


@login_required
def delete_grade(request, grade_id):
    active_role = request.session.get('active_role', request.user.role)
    if active_role != 'it_admin':
        return redirect('dashboard')
    grade = get_object_or_404(Grade, id=grade_id)
    grade.delete()
    messages.success(request, 'Grade deleted successfully!')
    return redirect('manage_grades')


@login_required
def manage_job_titles(request):
    active_role = request.session.get('active_role', request.user.role)
    if active_role != 'it_admin':
        return redirect('dashboard')

    job_titles = JobTitle.objects.all()
    departments = Department.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        department_id = request.POST.get('department')
        if name:
            if JobTitle.objects.filter(name__iexact=name.strip()).exists():
                messages.error(request, f'A job title named "{name}" already exists.')
            else:
                job_title = JobTitle(name=name.strip())
                if department_id:
                    job_title.department = Department.objects.get(id=department_id)
                job_title.save()
                messages.success(request, f'Job Title "{name}" created successfully!')
                return redirect('manage_job_titles')

    return render(request, 'accounts/manage_job_titles.html', {
        'job_titles': job_titles,
        'departments': departments,
    })


@login_required
def edit_job_title(request, job_title_id):
    active_role = request.session.get('active_role', request.user.role)
    if active_role != 'it_admin':
        return redirect('dashboard')

    job_title = get_object_or_404(JobTitle, id=job_title_id)
    departments = Department.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        department_id = request.POST.get('department')
        if name:
            if JobTitle.objects.filter(name__iexact=name.strip()).exclude(id=job_title.id).exists():
                messages.error(request, f'A job title named "{name}" already exists.')
            else:
                job_title.name = name.strip()
                job_title.department = Department.objects.get(id=department_id) if department_id else None
                job_title.save()
                messages.success(request, f'Job Title "{name}" updated successfully!')
                return redirect('manage_job_titles')

    return render(request, 'accounts/edit_job_title.html', {
        'job_title': job_title,
        'departments': departments,
    })


@login_required
def delete_job_title(request, job_title_id):
    active_role = request.session.get('active_role', request.user.role)
    if active_role != 'it_admin':
        return redirect('dashboard')
    job_title = get_object_or_404(JobTitle, id=job_title_id)
    job_title.delete()
    messages.success(request, 'Job Title deleted successfully!')
    return redirect('manage_job_titles')


@login_required
def user_profile(request):
    user = request.user
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.phone = request.POST.get('phone')
        if request.FILES.get('profile_photo'):
            user.profile_photo = request.FILES.get('profile_photo')
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('user_profile')

    return render(request, 'accounts/profile.html', {'user': user})