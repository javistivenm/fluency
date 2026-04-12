from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    return redirect('accounts:login')


@login_required
def dashboard(request):
    return render(request, 'core/dashboard.html')
