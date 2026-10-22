from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Announcement, Batch, Course, CourseNote


class PublicCoursePagesTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            title='Python Development',
            duration='4 months',
            syllabus='Python basics\nWeb development',
        )
        self.batch = Batch.objects.create(
            course=self.course,
            name='November cohort',
            month=11,
            year=2026,
            google_form_url='https://docs.google.com/forms/d/example',
            registrations_open=True,
        )
        Announcement.objects.create(message='Admissions are open')
        CourseNote.objects.create(
            course=self.course,
            title='Prerequisites',
            content='Basic computer skills recommended.',
        )

    def test_announcement_is_visible_on_public_pages(self):
        for url in ('/', '/courses/', '/registration/', '/about/', '/contact/'):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'Admissions are open')

    def test_open_batch_shows_registration_link_on_public_pages(self):
        for url in ('/', '/courses/', '/registration/'):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(response, self.batch.google_form_url)
                self.assertContains(response, 'Register here')

    def test_closed_batch_hides_google_form_link(self):
        self.batch.registrations_open = False
        self.batch.save(update_fields=('registrations_open',))

        response = self.client.get('/registration/')

        self.assertContains(response, 'Closed')
        self.assertNotContains(response, self.batch.google_form_url)

    def test_course_note_is_visible_and_searchable(self):
        response = self.client.get('/courses/')

        self.assertContains(response, 'Prerequisites')
        self.assertContains(response, 'Basic computer skills recommended.')

        response = self.client.get('/courses/?q=prerequisites')

        self.assertContains(response, 'Python Development')
        self.assertContains(response, 'Prerequisites')


class StaffCourseManagementTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.staff = user_model.objects.create_user(
            username='staff',
            password='secure-test-password',
            is_staff=True,
        )

    def test_login_redirects_to_requested_staff_page(self):
        response = self.client.post(
            '/staff-login/?next=/admin-course-add/',
            {
                'username': 'staff',
                'password': 'secure-test-password',
                'next': '/admin-course-add/',
            },
        )

        self.assertRedirects(response, '/admin-course-add/')

    def test_login_rejects_external_next_url(self):
        response = self.client.post(
            '/staff-login/',
            {
                'username': 'staff',
                'password': 'secure-test-password',
                'next': 'https://example.com/',
            },
        )

        self.assertRedirects(response, reverse('admin_dashboard'))

    def test_course_add_creates_course_and_first_batch(self):
        self.client.force_login(self.staff)

        response = self.client.post(reverse('admin_course_add'), {
            'title': 'Java Development',
            'category': 'Software',
            'duration': '6 months',
            'description': 'Practical Java training.',
            'syllabus': 'Core Java\nSpring',
            'batch_name': 'January cohort',
            'month': '1',
            'year': '2027',
            'google_form_url': 'https://docs.google.com/forms/d/java',
        })

        self.assertRedirects(response, reverse('admin_dashboard'))
        course = Course.objects.get(title='Java Development')
        batch = course.batches.get()
        self.assertEqual(batch.month_year, 'January 2027')
        self.assertEqual(batch.google_form_url, 'https://docs.google.com/forms/d/java')
        self.assertFalse(batch.registrations_open)

    def test_staff_can_toggle_registration_status(self):
        self.client.force_login(self.staff)
        course = Course.objects.create(title='Data Science', duration='5 months')
        batch = Batch.objects.create(
            course=course,
            name='March cohort',
            month=3,
            year=2027,
            google_form_url='https://docs.google.com/forms/d/data',
        )

        self.client.post(
            reverse('batch_registration_toggle', args=(batch.pk,)),
            {'action': 'open'},
        )
        batch.refresh_from_db()
        self.assertTrue(batch.registrations_open)

        self.client.post(
            reverse('batch_registration_toggle', args=(batch.pk,)),
            {'action': 'close'},
        )
        batch.refresh_from_db()
        self.assertFalse(batch.registrations_open)

    def test_staff_can_publish_and_delete_course_notes(self):
        self.client.force_login(self.staff)
        course = Course.objects.create(title='Data Science', duration='5 months')

        response = self.client.post(reverse('course_note_add'), {
            'course': course.pk,
            'title': 'Materials',
            'content': 'Bring a laptop.',
            'display_order': 0,
        })

        self.assertRedirects(response, reverse('admin_dashboard'))
        note = course.notes.get()
        self.assertEqual(note.content, 'Bring a laptop.')

        response = self.client.post(reverse('course_note_delete', args=(note.pk,)))

        self.assertRedirects(response, reverse('admin_dashboard'))
        self.assertFalse(CourseNote.objects.filter(pk=note.pk).exists())

    def test_non_staff_cannot_access_dashboard_or_change_registrations(self):
        user_model = get_user_model()
        regular_user = user_model.objects.create_user(
            username='student',
            password='secure-test-password',
        )
        self.client.force_login(regular_user)

        response = self.client.get(reverse('admin_dashboard'))

        self.assertRedirects(response, '/staff-login/?next=/admin-dashboard/')

        response = self.client.post(reverse('course_note_add'), {
            'course': '',
            'title': 'Unauthorized note',
            'content': 'This should not be saved.',
            'display_order': 0,
        })

        self.assertRedirects(response, '/staff-login/?next=/course-note/add/')
        self.assertFalse(CourseNote.objects.filter(title='Unauthorized note').exists())
