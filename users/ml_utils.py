import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import timedelta
from django.db.models import Avg
from workouts.models import TrainingSession
from meals.models import NutritionLog

def analyze_performance_trend(user):
    """
    Analyzes the user's recent training performance trend using Linear Regression.
    Returns a dictionary or string with the insight.
    """
    
    # 1. Fetch Data (Recent 20 sessions max)
    sessions = TrainingSession.objects.filter(user=user).order_by('date')
    if not sessions.exists():
        return None

    # Determine main discipline from the most recent session
    # (Assuming single-sport focus for simplicity in this MVP)
    latest_session = sessions.last()
    discipline = latest_session.discipline
    athlete_type = latest_session.athlete_type # 'runner', 'jumper', 'thrower'
    
    # Filter sessions for this discipline only
    relevant_sessions = sessions.filter(discipline=discipline)
    
    # Needs enough data points for regression
    if relevant_sessions.count() < 2:
        return "<b>AI Trend Analysis:</b> Not enough data to classify trend yet (need 2+ sessions)."
    
    # 2. Extract Data into DataFrame
    data = []
    for s in relevant_sessions:
        metric = None
        if hasattr(s, 'runnersession'): metric = s.runnersession.time_seconds
        elif hasattr(s, 'jumpersession'): metric = s.jumpersession.best_jump_m
        elif hasattr(s, 'throwersession'): metric = s.throwersession.best_throw_m
        
        if metric is not None and metric > 0:
            data.append({
                'date': s.date,
                'metric': metric
            })
            
    df = pd.DataFrame(data)
    if len(df) < 2:
        return "<b>AI Trend Analysis:</b> Not enough metric data available."
        
    # 3. Feature Engineering
    # Convert date to 'days since first session' for regression
    df['date'] = pd.to_datetime(df['date'])
    start_date = df['date'].min()
    df['days'] = (df['date'] - start_date).dt.days
    
    X = df[['days']] # Feature matrix
    y = df['metric'] # Target vector
    
    # 4. Train Model (Per Athlete)
    model = LinearRegression()
    model.fit(X, y)
    
    slope = model.coef_[0]
    
    # 5. Determine Trend Label
    # Slope = change in metric per day
    trend_label = "Stable"
    explanation = ""
    
    # Threshold for 'Stability' - arbitrary small number
    threshold = 0.001 
    
    if athlete_type == 'runner':
        # Runner: Time decrease (negative slope) is GOOD
        if slope < -threshold: trend_label = "Improving"
        elif slope > threshold: trend_label = "Declining"
    else:
        # Jumper/Thrower: Distance increase (positive slope) is GOOD
        if slope > threshold: trend_label = "Improving"
        elif slope < -threshold: trend_label = "Declining"
        
    # 6. Integrated Nutrition Context
    # Fetch average carbs for the same period
    nutrition_qs = NutritionLog.objects.filter(
        user=user, 
        date__gte=start_date, 
        date__lte=df['date'].max()
    )
    avg_carbs = nutrition_qs.aggregate(Avg('carbohydrates_g'))['carbohydrates_g__avg'] or 0
    avg_protein = nutrition_qs.aggregate(Avg('protein_g'))['protein_g__avg'] or 0
    
    # 7. Formulate Output
    # No "Prediction", just Classification of recent trend
    color = "black"
    if trend_label == "Improving": color = "green"
    elif trend_label == "Declining": color = "red"
    
    msg = f"<b>AI Trend Classification:</b> <strong style='color:{color}'>{trend_label}</strong><br>"
    msg += f"Based on linear analysis of your last {len(df)} sessions ({discipline}).<br>"
    msg += f"<small>Recent context: Avg Daily Carbs: {avg_carbs:.0f}g, Protein: {avg_protein:.0f}g during this period.</small>"
    
    return msg
