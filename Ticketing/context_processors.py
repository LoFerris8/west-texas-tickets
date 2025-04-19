from .models import Theater

# Adding a context processor saves us from having to include "theater = Theater.objects.all()" in every single view
def all_theaters(request):  
    return {
        'theaters': Theater.objects.all()
    }
