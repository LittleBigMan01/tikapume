from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import LeaveType, LeaveGradeDays, LeaveBalance, LeaveApplication, PublicHoliday
from .utils import calculate_working_days
from accounts.models import CustomUser, Grade
from django.db import models
from django.db.models import Q
import datetime


@login_required
def manage_leave_types(request):
    active_role = request.session.get('active_role', request.user.role)
    if active_role != 'it_admin':
        return redirect('dashboard')

    leave_types = LeaveType.objects.all()
    grade_days = LeaveGradeDays.objects.all().order_by('leave_type', 'grade')
    grades = Grade.objects.all()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_leave_type':
            name = request.POST.get('name')
            description = request.POST.get('description')
            if name:
                if LeaveType.objects.filter(name__iexact=name.strip()).exists():
                    messages.error(request, f'A leave type named "{name}" already exists.')
                else:
                    LeaveType.objects.create(
                        name=name.strip(),
                        description=description,
                    )
                    messages.success(request, f'Leave type "{name}" created successfully!')
                    return redirect('manage_leave_types')

        elif action == 'set_grade_days':
            leave_type_id = request.POST.get('leave_type')
            grade_id = request.POST.get('grade')
            days = request.POST.get('days')

            leave_type = get_object_or_404(LeaveType, id=leave_type_id)
            grade = get_object_or_404(Grade, id=grade_id)

            gd, created = LeaveGradeDays.objects.get_or_create(
                leave_type=leave_type,
                grade=grade,
                defaults={'days': days}
            )
            if not created:
                gd.days = days
                gd.save()
                messages.success(request, f'Days updated for {grade.name} — {leave_type.name}!')
            else:
                messages.success(request, f'Days set for {grade.name} — {leave_type.name}!')

            return redirect('manage_leave_types')

    return render(request, 'leaves/manage_leave_types.html', {
        'leave_types': leave_types,
        'grade_days': grade_days,
        'grades': grades,
    })


@login_required
def manage_public_holidays(request):
    active_role = request.session.get('active_role', request.user.role)
    if active_role != 'it_admin':
        return redirect('dashboard')

    holidays = PublicHoliday.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        date = request.POST.get('date')
        if name and date:
            if PublicHoliday.objects.filter(date=date).exists():
                messages.error(request, f'A public holiday is already set for {date}.')
            else:
                PublicHoliday.objects.create(name=name.strip(), date=date)
                messages.success(request, f'Public holiday "{name}" added successfully!')
                return redirect('manage_public_holidays')

    return render(request, 'leaves/manage_public_holidays.html', {
        'holidays': holidays,
    })


@login_required
def delete_public_holiday(request, holiday_id):
    active_role = request.session.get('active_role', request.user.role)
    if active_role != 'it_admin':
        return redirect('dashboard')
    holiday = get_object_or_404(PublicHoliday, id=holiday_id)
    holiday.delete()
    messages.success(request, 'Public holiday removed successfully!')
    return redirect('manage_public_holidays')


@login_required
def manage_balances(request):
    active_role = request.session.get('active_role', request.user.role)
    if active_role != 'it_admin':
        return redirect('dashboard')

    employees = CustomUser.objects.filter(
        Q(role='employee') | Q(secondary_role='employee') |
        Q(role='hr') | Q(role='approver') | Q(role='it_admin')
    ).order_by('first_name')
    leave_types = LeaveType.objects.all()
    balances = LeaveBalance.objects.all().order_by('user', 'leave_type')

    if request.method == 'POST':
        user_id = request.POST.get('user')
        leave_type_id = request.POST.get('leave_type')
        total_days = request.POST.get('total_days')
        year = request.POST.get('year')

        user = get_object_or_404(CustomUser, id=user_id)
        leave_type = get_object_or_404(LeaveType, id=leave_type_id)

        balance, created = LeaveBalance.objects.get_or_create(
            user=user,
            leave_type=leave_type,
            year=year,
            defaults={'total_days': total_days}
        )

        if not created:
            balance.total_days = total_days
            balance.save()
            messages.success(request, f'Balance updated for {user.get_full_name()}!')
        else:
            messages.success(request, f'Balance assigned to {user.get_full_name()} successfully!')

        return redirect('manage_balances')

    return render(request, 'leaves/manage_balances.html', {
        'employees': employees,
        'leave_types': leave_types,
        'balances': balances,
        'current_year': datetime.date.today().year,
    })


@login_required
def apply_leave(request):
    active_role = request.session.get('active_role', request.user.role)
    if active_role not in ['employee', 'it_admin']:
        return redirect('dashboard')

    leave_types = LeaveType.objects.all()
    current_year = datetime.date.today().year
    leave_balances = LeaveBalance.objects.filter(
        user=request.user,
        year=current_year
    )

    # Get supervisors — users with approver role or secondary role
    supervisors = CustomUser.objects.filter(
    is_supervisor = True
    ).exclude(id=request.user.id)
    

    if request.method == 'POST':
        leave_type_id = request.POST.get('leave_type')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = request.POST.get('reason')
        chosen_supervisor_id = request.POST.get('chosen_supervisor')
        is_special_request = bool(request.POST.get('is_special_request'))
        special_request_reason = request.POST.get('special_request_reason', '').strip()

        leave_type = get_object_or_404(LeaveType, id=leave_type_id)
        start = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

        if end < start:
            messages.error(request, 'End date cannot be before start date.')
            return redirect('apply_leave')

        # 7-day advance notice rule, unless this is a special request
        days_until_start = (start - datetime.date.today()).days
        if not is_special_request and days_until_start < 7:
            messages.error(
                request,
                'Leave must be applied for at least 7 days in advance. '
                'If this is urgent, tick "Special Request" and provide a reason.'
            )
            return redirect('apply_leave')

        if is_special_request and not special_request_reason:
            messages.error(request, 'Please provide a reason for the special request.')
            return redirect('apply_leave')

        total_days = calculate_working_days(start, end)
        if total_days == 0:
            messages.error(
                request,
                'The selected date range contains no working days '
                '(all weekends/public holidays).'
            )
            return redirect('apply_leave')

        try:
            balance = LeaveBalance.objects.get(
                user=request.user,
                leave_type=leave_type,
                year=current_year
            )
            if balance.remaining_days < total_days:
                messages.error(request, f'Insufficient leave balance! You have {balance.remaining_days} days remaining but requested {total_days} working days.')
                return redirect('apply_leave')
        except LeaveBalance.DoesNotExist:
            messages.error(request, 'You have no leave balance assigned for this leave type. Contact IT Administrator.')
            return redirect('apply_leave')

        chosen_supervisor = None
        if chosen_supervisor_id:
            chosen_supervisor = get_object_or_404(CustomUser, id=chosen_supervisor_id)

        LeaveApplication.objects.create(
            applicant=request.user,
            leave_type=leave_type,
            start_date=start,
            end_date=end,
            total_days=total_days,
            reason=reason,
            is_special_request=is_special_request,
            special_request_reason=special_request_reason,
            status='pending',
            chosen_supervisor=chosen_supervisor,
        )

        messages.success(request, 'Leave application submitted! Your supervisor will review it first.')
        return redirect('my_applications')

    return render(request, 'leaves/apply_leave.html', {
        'leave_types': leave_types,
        'leave_balances': leave_balances,
        'supervisors': supervisors,
    })


@login_required
def my_applications(request):
    active_role = request.session.get('active_role', request.user.role)
    if active_role not in ['employee', 'it_admin']:
        return redirect('dashboard')

    applications = LeaveApplication.objects.filter(
        applicant=request.user
    ).order_by('-applied_at')

    return render(request, 'leaves/my_applications.html', {
        'applications': applications,
    })


@login_required
def all_applications(request):
    active_role = request.session.get('active_role', request.user.role)
    if active_role not in ['it_admin', 'hr', 'approver']:
        return redirect('dashboard')

    applications = LeaveApplication.objects.all().order_by('-applied_at')

    pending_count = applications.filter(status='pending').count()
    approved_count = applications.filter(status='approved').count()
    declined_count = applications.filter(status='declined').count()
    forwarded_count = applications.filter(status='forwarded_to_approver').count()
    supervisor_approved_count = applications.filter(status='supervisor_approved').count()

    return render(request, 'leaves/all_applications.html', {
        'applications': applications,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'declined_count': declined_count,
        'forwarded_count': forwarded_count,
        'supervisor_approved_count': supervisor_approved_count,
    })


@login_required
def hr_pending_requests(request):
    active_role = request.session.get('active_role', request.user.role)
    if active_role != 'hr':
        return redirect('dashboard')

    # HR sees supervisor approved requests
    pending = LeaveApplication.objects.filter(
        status='supervisor_approved'
    ).order_by('-applied_at')

    return render(request, 'leaves/hr_pending_requests.html', {
        'applications': pending,
    })


@login_required
def hr_forward_to_approver(request, application_id):
    active_role = request.session.get('active_role', request.user.role)
    if active_role != 'hr':
        return redirect('dashboard')

    application = get_object_or_404(LeaveApplication, id=application_id)
    approvers = CustomUser.objects.filter(
        Q(role='approver') | Q(secondary_role='approver')
    )

    if request.method == 'POST':
        hr_comment = request.POST.get('hr_comment', '')
        chosen_approver_id = request.POST.get('chosen_approver')

        application.status = 'forwarded_to_approver'
        application.hr_comment = hr_comment

        if chosen_approver_id:
            application.chosen_approver = get_object_or_404(
                CustomUser, id=chosen_approver_id
            )

        application.save()

        from notifications.models import Notification

        # Notify chosen approver
        if application.chosen_approver:
            Notification.objects.create(
                recipient=application.chosen_approver,
                sender=request.user,
                leave_application=application,
                notification_type='leave_forwarded',
                message=f'{application.applicant.get_full_name()} has applied for {application.leave_type.name} from {application.start_date} to {application.end_date}. Please review.'
            )

        # Notify applicant
        Notification.objects.create(
            recipient=application.applicant,
            sender=request.user,
            leave_application=application,
            notification_type='leave_forwarded',
            message=f'Your leave request has been reviewed by HR and forwarded to {application.chosen_approver.get_full_name() if application.chosen_approver else "the Approver"} for approval.'
        )

        messages.success(request, 'Leave request forwarded to Approver successfully!')
        return redirect('hr_pending_requests')

    return render(request, 'leaves/hr_forward.html', {
        'application': application,
        'approvers': approvers,
    })


@login_required
def supervisor_pending_requests(request):
    active_role = request.session.get('active_role', request.user.role)
    if active_role not in ['employee', 'it_admin'] or not request.user.is_supervisor:
        return redirect('dashboard')
    pending = LeaveApplication.objects.filter(
        status='pending',
        chosen_supervisor=request.user
    ).order_by('-applied_at')

    return render(request, 'leaves/supervisor_pending_requests.html', {
        'applications': pending,
    })


@login_required
def supervisor_action(request, application_id):
    active_role = request.session.get('active_role', request.user.role)
    if active_role not in ['employee', 'it_admin'] or not request.user.is_supervisor:
        return redirect('dashboard')

    application = get_object_or_404(LeaveApplication, id=application_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        supervisor_comment = request.POST.get('supervisor_comment', '')
        application.supervisor_comment = supervisor_comment

        from notifications.models import Notification

        if action == 'approve':
            application.status = 'supervisor_approved'
            # Notify HR
            hr_users = CustomUser.objects.filter(role='hr')
            for hr in hr_users:
                Notification.objects.create(
                    recipient=hr,
                    sender=request.user,
                    leave_application=application,
                    notification_type='leave_forwarded',
                    message=f'{application.applicant.get_full_name()} leave request has been approved by supervisor {request.user.get_full_name()}. Please review and forward to Approver.'
                )
            # Notify applicant
            Notification.objects.create(
                recipient=application.applicant,
                sender=request.user,
                leave_application=application,
                notification_type='leave_forwarded',
                message=f'Your leave request has been approved by your supervisor {request.user.get_full_name()} and forwarded to HR.'
            )
            messages.success(request, 'Leave approved and forwarded to HR!')

        elif action == 'decline':
            application.status = 'supervisor_declined'
            # Notify applicant
            Notification.objects.create(
                recipient=application.applicant,
                sender=request.user,
                leave_application=application,
                notification_type='leave_declined',
                message=f'Your leave request has been declined by your supervisor {request.user.get_full_name()}. Reason: {supervisor_comment}'
            )
            messages.success(request, 'Leave declined.')

        application.save()
        return redirect('supervisor_pending_requests')

    return render(request, 'leaves/supervisor_action.html', {
        'application': application,
    })


@login_required
def approver_pending_requests(request):
    active_role = request.session.get('active_role', request.user.role)
    if active_role != 'approver':
        return redirect('dashboard')

    pending = LeaveApplication.objects.filter(
        status='forwarded_to_approver',
        chosen_approver=request.user
    ).order_by('-applied_at')

    return render(request, 'leaves/approver_pending_requests.html', {
        'applications': pending,
    })


@login_required
def approve_decline_leave(request, application_id):
    active_role = request.session.get('active_role', request.user.role)
    if active_role != 'approver':
        return redirect('dashboard')

    application = get_object_or_404(LeaveApplication, id=application_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        approver_comment = request.POST.get('approver_comment', '')
        application.approver_comment = approver_comment

        if action == 'approve':
            application.status = 'approved'
            try:
                balance = LeaveBalance.objects.get(
                    user=application.applicant,
                    leave_type=application.leave_type,
                    year=application.start_date.year
                )
                balance.used_days += application.total_days
                balance.save()
            except LeaveBalance.DoesNotExist:
                pass

        elif action == 'decline':
            application.status = 'declined'

        application.save()

        from notifications.models import Notification

        # Notify HR
        hr_users = CustomUser.objects.filter(role='hr')
        for hr in hr_users:
            Notification.objects.create(
                recipient=hr,
                sender=request.user,
                leave_application=application,
                notification_type='leave_approved' if action == 'approve' else 'leave_declined',
                message=f'Leave request for {application.applicant.get_full_name()} has been {application.status} by {request.user.get_full_name()}. Please notify the employee.'
            )

        # Notify applicant
        Notification.objects.create(
            recipient=application.applicant,
            sender=request.user,
            leave_application=application,
            notification_type='leave_approved' if action == 'approve' else 'leave_declined',
            message=f'Your leave request for {application.leave_type.name} from {application.start_date} to {application.end_date} has been {application.status} by {request.user.get_full_name()}.'
        )

        messages.success(request, f'Leave {application.status} successfully!')
        return redirect('approver_pending_requests')

    return render(request, 'leaves/approve_decline.html', {
        'application': application,
    })