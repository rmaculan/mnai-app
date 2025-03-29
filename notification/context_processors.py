from notification.models import Notification

def notifications_processor(request):
    """
    Context processor that adds notifications to the request context
    to make them available across all templates.
    """
    if request.user.is_authenticated:
        return {
            'notifications': Notification.objects.filter(user=request.user).order_by('-date'),
        }
    return {'notifications': []}
