from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .models import Level
from .selectors import get_or_create_daily_challenge, get_selected_level


@login_required
def home(request):
    levels = Level.objects.filter(is_active=True)
    selected_level = get_selected_level(request)
    return render(
        request,
        'fluency/home.html',
        {
            'levels': levels,
            'selected_level': selected_level,
        },
    )


@login_required
def set_level(request):
    if request.method != 'POST':
        return redirect('fluency:home')

    level_code = request.POST.get('level_code', '').strip().upper()
    level = Level.objects.filter(code=level_code, is_active=True).first()

    if level is None:
        messages.error(request, 'Please choose a valid level before starting your daily challenge.')
        return redirect('fluency:home')

    request.session['selected_level_code'] = level.code
    messages.success(request, f'Your practice level is now set to {level.code}.')
    return redirect('fluency:daily-challenge')


@login_required
def daily_challenge(request):
    selected_level = get_selected_level(request)
    if selected_level is None:
        messages.info(request, 'Choose your level first to unlock today\'s writing challenge.')
        return redirect('fluency:home')

    challenge = get_or_create_daily_challenge(selected_level)
    return render(
        request,
        'fluency/daily_challenge.html',
        {
            'selected_level': selected_level,
            'challenge': challenge,
        },
    )
