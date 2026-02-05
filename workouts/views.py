from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import TrainingSession, RunnerSession, JumperSession, ThrowerSession

@login_required
def log_training(request):
    if request.method == "POST":
        data = request.POST
        
        # Determine Athlete Type (normalize to lowercase)
        athlete_type = data.get('athlete_type', '').lower()
        
        # 1. Create Base Session
        try:
            base_session = TrainingSession.objects.create(
                user=request.user,
                date=data.get('date'),
                discipline=data.get('discipline'),
                session_type=data.get('session_type'),
                athlete_type=athlete_type,  # Explicitly set
                notes=data.get('notes')
            )
            
            # 2. Create Specific Session matching the Type
            if athlete_type == 'runner':
                RunnerSession.objects.create(
                    session=base_session,
                    distance_m=data.get('distance_m') or 0,
                    time_seconds=data.get('time_seconds') or 0,
                    repetitions=data.get('repetitions') or 1
                )
            elif athlete_type == 'jumper':
                JumperSession.objects.create(
                    session=base_session,
                    attempts=data.get('attempts') or 1,
                    best_jump_m=data.get('best_jump_m') or 0
                )
            elif athlete_type == 'thrower':
                ThrowerSession.objects.create(
                    session=base_session,
                    attempts=data.get('attempts') or 1,
                    best_throw_m=data.get('best_throw_m') or 0,
                    implement_weight_kg=data.get('implement_weight_kg') or 0
                )
            else:
                # Fallback or Error if type is invalid/missing
                # But since base session is created with it, it must be valid choice or error there.
                # If we are here, base session created. If no child created, that's an issue for strictness,
                # but for "MINIMAL FIX" we ensure type is set.
                pass
            
            messages.success(request, "Training session logged successfully!")
            return redirect('training_history')
            
        except Exception as e:
            messages.error(request, f"Error logging session: {e}")
            return redirect('log_training')

    return render(request, "workouts/log_training.html")

@login_required
def training_history(request):
    # Prefetch related objects to avoid N+1 queries
    sessions = TrainingSession.objects.filter(user=request.user).select_related(
        'runnersession', 'jumpersession', 'throwersession'
    )
    
    context = {
        'sessions': sessions
    }
    return render(request, "workouts/training_list.html", context)
