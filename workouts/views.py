from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import TrainingSession, RunnerSession, JumperSession, ThrowerSession

@login_required
@login_required
def log_training(request):
    if request.method == "POST":
        data = request.POST

        try:
            # Create base training session with NEW required fields
            base_session = TrainingSession.objects.create(
                user=request.user,
                date=data.get('date'),
                discipline=data.get('discipline'),
                session_type=data.get('session_type'),
                duration_minutes=float(data.get('duration_minutes') or 0),
                intensity=data.get('intensity'),
                rpe=int(data.get('rpe') or 5),
                notes=data.get('notes')
            )

            athlete_type = data.get('athlete_type', '').lower()

            # Create performance child object
            if athlete_type == 'runner':
                RunnerSession.objects.create(
                    session=base_session,
                    distance_m=float(data.get('distance_m') or 0),
                    time_seconds=float(data.get('time_seconds') or 0),
                    repetitions=int(data.get('repetitions') or 1)
                )

            elif athlete_type == 'jumper':
                JumperSession.objects.create(
                    session=base_session,
                    attempts=int(data.get('attempts') or 1),
                    best_jump_m=float(data.get('best_jump_m') or 0)
                )

            elif athlete_type == 'thrower':
                ThrowerSession.objects.create(
                    session=base_session,
                    attempts=int(data.get('attempts') or 1),
                    best_throw_m=float(data.get('best_throw_m') or 0),
                    implement_weight_kg=float(data.get('implement_weight_kg') or 0)
                )

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
