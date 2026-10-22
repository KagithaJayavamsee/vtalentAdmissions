from .models import Announcement


def site_announcements(request):
    return {'announcements': Announcement.objects.all()}
