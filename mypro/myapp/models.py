from django.db import models


class Course(models.Model):
    title = models.CharField(max_length=150)
    category = models.CharField(max_length=100, blank=True)
    duration = models.CharField(max_length=80)
    description = models.TextField(blank=True)
    syllabus = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ('display_order', 'title')

    def __str__(self):
        return self.title

    @property
    def syllabus_items(self):
        return [item.strip() for item in self.syllabus.splitlines() if item.strip()]


class Batch(models.Model):
    MONTH_CHOICES = (
        ('1', 'January'),
        ('2', 'February'),
        ('3', 'March'),
        ('4', 'April'),
        ('5', 'May'),
        ('6', 'June'),
        ('7', 'July'),
        ('8', 'August'),
        ('9', 'September'),
        ('10', 'October'),
        ('11', 'November'),
        ('12', 'December'),
    )

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='batches')
    name = models.CharField(max_length=100)
    month = models.CharField(max_length=30, choices=MONTH_CHOICES)
    year = models.PositiveSmallIntegerField()
    duration = models.CharField(max_length=80, blank=True)
    google_form_url = models.URLField(max_length=500, blank=True)
    registrations_open = models.BooleanField(default=False)

    class Meta:
        ordering = ('year', 'month', 'name')

    def __str__(self):
        return f'{self.course.title} - {self.name}'

    @property
    def month_year(self):
        return f'{self.get_month_display()} {self.year}'

    @property
    def can_register(self):
        return self.registrations_open and bool(self.google_form_url)


class CourseNote(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=150)
    content = models.TextField()
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('display_order', 'id')

    def __str__(self):
        return f'{self.course.title} - {self.title}'


class Announcement(models.Model):
    message = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at', '-id')

    def __str__(self):
        return self.message
