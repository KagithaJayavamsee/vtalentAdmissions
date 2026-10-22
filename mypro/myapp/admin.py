from django.contrib import admin

from .models import Announcement, Batch, Course, CourseNote


class BatchInline(admin.TabularInline):
    model = Batch
    extra = 0


class CourseNoteInline(admin.TabularInline):
    model = CourseNote
    extra = 0


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'duration', 'display_order')
    search_fields = ('title', 'category', 'description', 'syllabus')
    inlines = (BatchInline, CourseNoteInline)


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'month', 'year', 'registrations_open')
    list_filter = ('registrations_open', 'year', 'month')
    search_fields = ('name', 'course__title')


@admin.register(CourseNote)
class CourseNoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'display_order', 'updated_at')
    list_filter = ('course',)
    search_fields = ('title', 'content', 'course__title')


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('message', 'created_at')
    search_fields = ('message',)
