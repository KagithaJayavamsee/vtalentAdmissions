from django import forms

from .models import Announcement, Batch, Course, CourseNote


def styled_fields(form, field_names):
    for name in field_names:
        form.fields[name].widget.attrs.setdefault('class', 'form-control')


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ('title', 'category', 'duration', 'display_order', 'description', 'syllabus')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
            'syllabus': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        styled_fields(self, self.fields)


class CourseCreateForm(CourseForm):
    batch_name = forms.CharField(max_length=100, label='First batch name')
    month = forms.TypedChoiceField(
        choices=Batch.MONTH_CHOICES,
        coerce=str,
        label='Batch month',
    )
    year = forms.IntegerField(min_value=2020, max_value=2100, label='Batch year')
    google_form_url = forms.URLField(
        max_length=500,
        required=False,
        label='Google Form link',
    )

    class Meta(CourseForm.Meta):
        fields = ('title', 'category', 'duration', 'description', 'syllabus')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['month'].widget.attrs['class'] = 'form-control'
        self.fields['google_form_url'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'https://docs.google.com/forms/...'}
        )
        for name in ('batch_name', 'year'):
            self.fields[name].widget.attrs['class'] = 'form-control'


class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = ('name', 'month', 'year', 'duration', 'google_form_url')
        widgets = {
            'year': forms.NumberInput(attrs={'min': 2020, 'max': 2100}),
            'google_form_url': forms.URLInput(
                attrs={'placeholder': 'https://docs.google.com/forms/...'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        styled_fields(self, self.fields)


class AddBatchForm(BatchForm):
    course = forms.ModelChoiceField(queryset=Course.objects.all(), label='Course')

    class Meta(BatchForm.Meta):
        fields = ('course', 'name', 'month', 'year', 'duration', 'google_form_url')


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ('message',)
        widgets = {
            'message': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'maxlength': 250,
                    'placeholder': 'Write a notice for every page',
                }
            )
        }


class CourseNoteForm(forms.ModelForm):
    class Meta:
        model = CourseNote
        fields = ('course', 'title', 'content', 'display_order')
        widgets = {'content': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        styled_fields(self, self.fields)
