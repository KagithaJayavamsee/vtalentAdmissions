from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.db import transaction
from django.db.models import Exists, OuterRef, Q
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import (
    AddBatchForm,
    AnnouncementForm,
    BatchForm,
    CourseCreateForm,
    CourseForm,
    CourseNoteForm,
)
from .models import Announcement, Batch, Course, CourseNote


def _staff_required(view):
    return user_passes_test(
        lambda user: user.is_authenticated and user.is_staff,
        login_url='staff_login',
    )(view)


def home(request):
    batches = Batch.objects.select_related('course').order_by('year', 'month', 'name')
    return render(request, 'home.html', {
        'batches': batches,
        'courses': Course.objects.prefetch_related('batches').all(),
        'batch_count': batches.count(),
    })


def courses(request):
    search_query = request.GET.get('q', '').strip()
    course_list = Course.objects.prefetch_related('batches', 'notes')
    if search_query:
        normalized_query = search_query.lower()
        matching_notes = CourseNote.objects.alias(
            search_title=Lower('title'),
            search_content=Lower('content'),
        ).filter(
            course_id=OuterRef('pk'),
        ).filter(
            Q(search_title__contains=normalized_query)
            | Q(search_content__contains=normalized_query)
        )
        course_list = course_list.alias(
            search_title=Lower('title'),
            search_category=Lower('category'),
            search_description=Lower('description'),
            search_syllabus=Lower('syllabus'),
        ).filter(
            Q(search_title__contains=normalized_query)
            | Q(search_category__contains=normalized_query)
            | Q(search_description__contains=normalized_query)
            | Q(search_syllabus__contains=normalized_query)
            | Q(Exists(matching_notes))
        )
    return render(request, 'courses.html', {
        'courses': course_list,
        'search_query': search_query,
    })


def registration(request):
    course_list = Course.objects.prefetch_related('batches').all()
    selected = request.GET.get('course', '')
    if selected and (not selected.isdecimal() or not course_list.filter(pk=selected).exists()):
        selected = ''
    return render(request, 'registration.html', {
        'courses': course_list,
        'selected_course_id': selected,
    })


def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')



def staff_login(request):
    next_url = request.POST.get('next') or request.GET.get('next', '')

    if not url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = ''

    if request.user.is_authenticated and request.user.is_staff:
        return redirect(next_url or 'admin_dashboard')

    error = None

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None and user.is_staff:
            login(request, user)
            return redirect(next_url or 'admin_dashboard')

        error = (
            'The username or password was not recognized, '
            'or the account is not staff.'
        )

    return render(
        request,
        'admin_login.html',
        {'error': error, 'next': next_url},
    )

@_staff_required
@require_POST
def staff_logout(request):
    logout(request)
    return redirect('home')


@_staff_required
def admin_dashboard(request):
    return render(request, 'admin.html', {
        'courses': Course.objects.prefetch_related('batches', 'notes').all(),
        'batch_form': AddBatchForm(),
        'note_form': CourseNoteForm(),
        'announcement_form': AnnouncementForm(),
        'all_announcements': Announcement.objects.all(),
    })


@_staff_required
def course_add(request):
    if request.method == 'POST':
        form = CourseCreateForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                course = form.save()
                Batch.objects.create(
                    course=course,
                    name=form.cleaned_data['batch_name'],
                    month=form.cleaned_data['month'],
                    year=form.cleaned_data['year'],
                    duration=course.duration,
                    google_form_url=form.cleaned_data['google_form_url'],
                )
            messages.success(request, 'Course and first batch added successfully.')
            return redirect('admin_dashboard')
    else:
        form = CourseCreateForm()
    return render(request, 'course_add.html', {'form': form})


@_staff_required
@require_POST
def course_edit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    form = CourseForm(request.POST, instance=course)
    if form.is_valid():
        form.save()
        messages.success(request, 'Course updated successfully.')
    else:
        messages.error(request, 'Course could not be updated. Check the required fields and try again.')
    return redirect('admin_dashboard')


@_staff_required
@require_POST
def course_delete(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    course.delete()
    messages.success(request, 'Course and its batches deleted.')
    return redirect('admin_dashboard')


@_staff_required
@require_POST
def batch_add(request):
    form = AddBatchForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, 'Batch added successfully.')
    else:
        messages.error(request, 'Batch could not be added. Check the details and try again.')
    return redirect('admin_dashboard')


@_staff_required
@require_POST
def batch_edit(request, batch_id):
    batch = get_object_or_404(Batch, pk=batch_id)
    form = BatchForm(request.POST, instance=batch)
    if form.is_valid():
        form.save()
        messages.success(request, 'Batch updated successfully.')
    else:
        messages.error(request, 'Batch could not be updated. Check the details and try again.')
    return redirect('admin_dashboard')


@_staff_required
@require_POST
def batch_delete(request, batch_id):
    batch = get_object_or_404(Batch, pk=batch_id)
    batch.delete()
    messages.success(request, 'Batch deleted successfully.')
    return redirect('admin_dashboard')


@_staff_required
@require_POST
def batch_registration_toggle(request, batch_id):
    batch = get_object_or_404(Batch, pk=batch_id)
    action = request.POST.get('action')
    if action == 'open':
        batch.registrations_open = True
    elif action == 'close':
        batch.registrations_open = False
    else:
        messages.error(request, 'Select whether to open or close registrations.')
        return redirect('admin_dashboard')
    batch.save(update_fields=('registrations_open',))
    messages.success(
        request,
        'Registrations opened.' if batch.registrations_open else 'Registrations closed.',
    )
    return redirect('admin_dashboard')


@_staff_required
@require_POST
def course_note_add(request):
    form = CourseNoteForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, 'Course note published.')
    else:
        messages.error(request, 'Course note could not be saved. Check the required fields.')
    return redirect('admin_dashboard')


@_staff_required
@require_POST
def course_note_edit(request, note_id):
    note = get_object_or_404(CourseNote, pk=note_id)
    form = CourseNoteForm(request.POST, instance=note)
    if form.is_valid():
        form.save()
        messages.success(request, 'Course note updated.')
    else:
        messages.error(request, 'Course note could not be updated. Check the required fields.')
    return redirect('admin_dashboard')


@_staff_required
@require_POST
def course_note_delete(request, note_id):
    note = get_object_or_404(CourseNote, pk=note_id)
    note.delete()
    messages.success(request, 'Course note deleted.')
    return redirect('admin_dashboard')


@_staff_required
@require_POST
def announcement_add(request):
    form = AnnouncementForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, 'Announcement published on the site.')
    else:
        messages.error(request, 'Announcement cannot be empty and must be 250 characters or fewer.')
    return redirect('admin_dashboard')


@_staff_required
@require_POST
def announcement_edit(request, notice_id):
    notice = get_object_or_404(Announcement, pk=notice_id)
    form = AnnouncementForm(request.POST, instance=notice)
    if form.is_valid():
        form.save()
        messages.success(request, 'Announcement updated.')
    else:
        messages.error(request, 'Announcement cannot be empty and must be 250 characters or fewer.')
    return redirect('admin_dashboard')


@_staff_required
@require_POST
def announcement_delete(request, notice_id):
    notice = get_object_or_404(Announcement, pk=notice_id)
    notice.delete()
    messages.success(request, 'Announcement deleted.')
    return redirect('admin_dashboard')
