from workouts.models import TrainingSession
from meals.models import NutritionLog
from django.db.models import Avg

def generate_training_plan(user):
    """
    Generates a deterministic, rule-based training plan based on the last 2+ sessions.
    RETURNS: HTML string bullet points.
    """
    # 1. Fetch recent sessions
    sessions = TrainingSession.objects.filter(user=user).order_by('-date')
    if sessions.count() < 2:
        return "Not enough data to generate a training plan. Please log at least 2 training sessions."

    # 2. Determine Focus based on most recent activity
    most_recent = sessions.first()
    discipline = most_recent.discipline
    athlete_type = most_recent.athlete_type
    
    # Compare last 2 sessions for trend
    s1 = sessions[0] # Newest
    s2 = sessions[1] # Previous

    plan_html = f"<b>Suggested Training Plan ({discipline}):</b><ul style='text-align: left; margin-top: 10px;'>"

    if athlete_type == 'runner':
        focus = "Speed Maintenance"
        # If time increased (slower) or distance decreased, focus on recovery/intensity
        current_metric = getattr(s1.runnersession, 'time_seconds', 0) if hasattr(s1, 'runnersession') else 0
        prev_metric = getattr(s2.runnersession, 'time_seconds', 0) if hasattr(s2, 'runnersession') else 0
        
        if current_metric > prev_metric and current_metric > 0:
             focus = "Speed & Anaerobic Power"
             plan_html += f"<li><b>Focus:</b> {focus} (Recent trend shows slight slowing).</li>"
             plan_html += "<li><b>Mon:</b> 5x 200m sprints @ 90% max effort (3min rest).</li>"
             plan_html += "<li><b>Tue:</b> Active recovery (light jog/cycle).</li>"
             plan_html += "<li><b>Wed:</b> Tempo run (20 min at threshold).</li>"
             plan_html += "<li><b>Fri:</b> Race simulation (broken intervals).</li>"
        else:
             focus = "Endurance & Consistency"
             plan_html += f"<li><b>Focus:</b> {focus} (Performance is stable/improving).</li>"
             plan_html += "<li><b>Mon:</b> 6x 400m intervals @ 80% effort.</li>"
             plan_html += "<li><b>Tue:</b> Long slow distance run.</li>"
             plan_html += "<li><b>Wed:</b> Technique drills & core.</li>"
             plan_html += "<li><b>Fri:</b> Speed endurance ladders.</li>"

    elif athlete_type == 'jumper':
        focus = "Technique"
        current_metric = getattr(s1.jumpersession, 'best_jump_m', 0) if hasattr(s1, 'jumpersession') else 0
        prev_metric = getattr(s2.jumpersession, 'best_jump_m', 0) if hasattr(s2, 'jumpersession') else 0

        if current_metric <= prev_metric:
            focus = "Explosive Power (Plyometrics)"
            plan_html += f"<li><b>Focus:</b> {focus} (Plateau detected).</li>"
            plan_html += "<li><b>Mon:</b> Depth jumps (3x5) + Box Jumps (3x8).</li>"
            plan_html += "<li><b>Tue:</b> Short approach technical jumps.</li>"
            plan_html += "<li><b>Wed:</b> Heavy Squats (5x5).</li>"
            plan_html += "<li><b>Fri:</b> Full approach practice.</li>"
        else:
            focus = "Technical Refinement"
            plan_html += f"<li><b>Focus:</b> {focus} (Good momentum).</li>"
            plan_html += "<li><b>Mon:</b> Approach rhythm drills.</li>"
            plan_html += "<li><b>Tue:</b> Flight phase mechanics.</li>"
            plan_html += "<li><b>Wed:</b> Power cleans & core.</li>"
            plan_html += "<li><b>Fri:</b> Simulation competition jumps.</li>"

    elif athlete_type == 'thrower':
        focus = "Strength Base"
        # Thrower logic usually balances weight vs speed
        plan_html += f"<li><b>Focus:</b> {focus} & Stability.</li>"
        plan_html += "<li><b>Mon:</b> Compound Lifts (Deadlift/Bench/Squat).</li>"
        plan_html += "<li><b>Tue:</b> Medicine ball throws (explosive).</li>"
        plan_html += "<li><b>Wed:</b> Technical throws (lighter implement).</li>"
        plan_html += "<li><b>Fri:</b> Full throws (measure distance).</li>"
    
    else:
        plan_html += "<li><b>Focus:</b> General Conditioning.</li>"
        plan_html += "<li><b>Mon:</b> Base Cardio.</li>"
        plan_html += "<li><b>Wed:</b> Full body strength.</li>"
        plan_html += "<li><b>Fri:</b> Mobility & Recovery.</li>"

    plan_html += "</ul>"
    return plan_html


def generate_diet_plan(user):
    """
    Generates a deterministic diet plan based on last 2+ logs.
    RETURNS: HTML string bullet points.
    """
    logs = NutritionLog.objects.filter(user=user).order_by('-date')
    if logs.count() < 2:
        return "Not enough data to generate a diet plan. Please log at least 2 meals."

    # Averages
    avgs = logs.aggregate(
        c=Avg('carbohydrates_g'), 
        p=Avg('protein_g'), 
        f=Avg('fats_g'),
        h=Avg('hydration_liters')
    )
    
    avg_c = avgs['c'] or 0
    avg_p = avgs['p'] or 0
    avg_f = avgs['f'] or 0
    avg_h = avgs['h'] or 0

    plan_html = f"<b>Suggested Diet Plan:</b><ul style='text-align: left; margin-top: 10px;'>"
    
    # Hydration
    if avg_h < 3.0:
        plan_html += f"<li><b>💧 Hydration ({avg_h:.1f}L):</b> Below target. Goal: 3.5L/day. Start with 500ml on waking.</li>"
    else:
        plan_html += f"<li><b>✅ Hydration ({avg_h:.1f}L):</b> Excellent. Keep maintaining this level.</li>"

    # Carbs
    if avg_c < 250:
        plan_html += f"<li><b>🍞 Carbs ({avg_c:.0f}g):</b> Low. Add pasta, rice, or potatoes to post-training meals to replenish glycogen.</li>"
    else:
         plan_html += f"<li><b>🍞 Carbs ({avg_c:.0f}g):</b> Optimal range. Focus on timing: complex carbs 3h pre-training.</li>"

    # Protein
    if avg_p < 110:
        plan_html += f"<li><b>🥩 Protein ({avg_p:.0f}g):</b> Needs boost. Target 120g+. Add eggs/shake at breakfast and lean meat at dinner.</li>"
    else:
        plan_html += f"<li><b>🥩 Protein ({avg_p:.0f}g):</b> Great level for synthesis. Ensure protein in every main meal.</li>"

    # General
    plan_html += f"<li><b>🥑 Fats ({avg_f:.0f}g):</b> Ensure sources are healthy (nuts, olive oil, fish).</li>"
    
    plan_html += "</ul>"
    return plan_html
