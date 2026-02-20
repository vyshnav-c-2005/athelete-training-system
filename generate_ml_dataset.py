"""
Athlete ML Dataset Generator
-----------------------------
Pulls data from the Django SQLite DB (users_userprofile + workouts_trainingsession),
transforms it into a clean ML-ready CSV: athlete_ml_dataset.csv
"""

import os, sys, django, datetime, math, warnings
import numpy as np
import pandas as pd

warnings.filterwarnings('ignore')

# ── Bootstrap Django ───────────────────────────────────────────────────────────
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'athlete_ai_system.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from users.models import UserProfile

# ── Step 1: Pull profile data ──────────────────────────────────────────────────
profiles = UserProfile.objects.select_related('user').all()
profile_rows = []
for p in profiles:
    try:
        dob  = p.date_of_birth
        gender = getattr(p, 'gender', None)
        height = getattr(p, 'height_cm', None)
        weight = getattr(p, 'weight_kg', None)
        sport  = getattr(p, 'sport', None)
        profile_rows.append({
            'user_id':    p.user.id,
            'gender':     gender,
            'height_cm':  height,
            'weight_kg':  weight,
            'primary_sport': sport,
            'date_of_birth': dob,
        })
    except Exception:
        continue

df_profiles = pd.DataFrame(profile_rows)
print(f"Profiles loaded: {len(df_profiles)}")

# ── Step 2: Pull training log data ─────────────────────────────────────────────
try:
    from workouts.models import TrainingSession
    sessions = TrainingSession.objects.all().values(
        'user_id', 'date', 'discipline', 'session_type',
        'duration_minutes', 'intensity', 'distance_m', 'effort_count'
    )
    df_training = pd.DataFrame(list(sessions))
    print(f"Training sessions loaded: {len(df_training)}")
except Exception as e:
    print(f"Could not load TrainingSession ({e}). Using synthetic training data.")
    df_training = pd.DataFrame()

# ── Step 3: If real data is sparse, augment / synthesise ──────────────────────
DISCIPLINES = {
    'TRACK':  ['100m Sprint', '200m Sprint', '400m Sprint', '800m Run', '1500m Run'],
    'JUMPS':  ['Long Jump', 'High Jump', 'Triple Jump'],
    'THROWS': ['Shot Put', 'Discus', 'Javelin', 'Hammer'],
}
ALL_DISCIPLINES = [d for group in DISCIPLINES.values() for d in group]
SESSION_TYPES   = ['Training', 'Competition', 'Recovery']
INTENSITIES     = ['Low', 'Medium', 'High']

np.random.seed(42)

# Targets: 2000 rows minimum
TARGET_ROWS = 2000

if len(df_profiles) == 0 or len(df_training) == 0:
    # Fully synthetic path
    print("Generating fully synthetic dataset...")
    N = TARGET_ROWS
    genders  = np.random.choice(['Male', 'Female'], N)
    heights  = np.round(np.random.uniform(155, 200, N), 1)
    weights  = np.round(np.random.uniform(45, 110, N), 1)
    ages     = np.random.randint(15, 41, N)
    discs    = np.random.choice(ALL_DISCIPLINES, N)
    s_types  = np.random.choice(SESSION_TYPES, N)
    durations= np.random.randint(20, 151, N)
    intens   = np.random.choice(INTENSITIES, N)
    dist_m   = np.random.randint(0, 15001, N)
    efforts  = np.random.randint(1, 21, N)

    df_merged = pd.DataFrame({
        'age': ages, 'gender': genders, 'height_cm': heights,
        'weight_kg': weights, 'discipline': discs,
        'session_type': s_types, 'duration_minutes': durations,
        'intensity': intens, 'distance_m': dist_m, 'effort_count': efforts,
    })

else:
    # Merge real profile + training data
    df_merged = df_training.merge(df_profiles, on='user_id', how='inner')

    # ── Age from DOB ──────────────────────────────────────────────────────────
    today = datetime.date.today()
    def calc_age(dob):
        if dob is None:
            return np.nan
        if isinstance(dob, str):
            try:
                dob = datetime.date.fromisoformat(dob)
            except Exception:
                return np.nan
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    df_merged['age'] = df_merged['date_of_birth'].apply(calc_age)
    df_merged.drop(columns=['date_of_birth', 'date', 'user_id', 'primary_sport'], errors='ignore', inplace=True)

    # ── Validate discipline values ────────────────────────────────────────────
    df_merged['discipline'] = df_merged['discipline'].apply(
        lambda d: d if d in ALL_DISCIPLINES else np.nan
    )
    df_merged.dropna(subset=['discipline'], inplace=True)

    # ── Augment if fewer than TARGET_ROWS ────────────────────────────────────
    if len(df_merged) < TARGET_ROWS:
        deficit = TARGET_ROWS - len(df_merged)
        print(f"Real data has {len(df_merged)} rows; synthesising {deficit} more...")
        synth_ages    = np.random.randint(15, 41, deficit)
        synth_genders = np.random.choice(['Male', 'Female'], deficit)
        synth_heights = np.round(np.random.uniform(155, 200, deficit), 1)
        synth_weights = np.round(np.random.uniform(45, 110, deficit), 1)
        synth_discs   = np.random.choice(ALL_DISCIPLINES, deficit)
        synth_stypes  = np.random.choice(SESSION_TYPES, deficit)
        synth_dur     = np.random.randint(20, 151, deficit)
        synth_intens  = np.random.choice(INTENSITIES, deficit)
        synth_dist    = np.random.randint(0, 15001, deficit)
        synth_efforts = np.random.randint(1, 21, deficit)

        df_synth = pd.DataFrame({
            'age': synth_ages, 'gender': synth_genders,
            'height_cm': synth_heights, 'weight_kg': synth_weights,
            'discipline': synth_discs, 'session_type': synth_stypes,
            'duration_minutes': synth_dur, 'intensity': synth_intens,
            'distance_m': synth_dist, 'effort_count': synth_efforts,
        })
        df_merged = pd.concat([df_merged, df_synth], ignore_index=True)

# ── Step 4: Handle missing values ─────────────────────────────────────────────
defaults = {
    'age':              25,
    'gender':           'Male',
    'height_cm':        175.0,
    'weight_kg':        70.0,
    'discipline':       '400m Sprint',
    'session_type':     'Training',
    'duration_minutes': 60,
    'intensity':        'Medium',
    'distance_m':       0,
    'effort_count':     5,
}
for col, val in defaults.items():
    if col in df_merged.columns:
        df_merged[col].fillna(val, inplace=True)

# Remove impossible rows
df_merged = df_merged[df_merged['height_cm'].between(140, 220)]
df_merged = df_merged[df_merged['weight_kg'].between(35, 130)]
df_merged = df_merged[df_merged['age'].between(14, 50)]
df_merged = df_merged[df_merged['duration_minutes'].between(5, 300)]
df_merged['distance_m']   = df_merged['distance_m'].clip(lower=0)
df_merged['effort_count'] = df_merged['effort_count'].clip(lower=0)

# ── Step 5: Compute target_calories ───────────────────────────────────────────
def compute_calories(row):
    gender   = row['gender']
    w        = float(row['weight_kg'])
    h        = float(row['height_cm'])
    a        = float(row['age'])
    dur      = float(row['duration_minutes'])
    intens   = row['intensity']
    s_type   = row['session_type']
    disc     = row['discipline']

    # Mifflin-St Jeor BMR
    if gender == 'Male':
        bmr = 10*w + 6.25*h - 5*a + 5
    else:
        bmr = 10*w + 6.25*h - 5*a - 161

    # Activity multiplier based on intensity
    activity_mult = {'Low': 1.375, 'Medium': 1.55, 'High': 1.725}.get(intens, 1.55)
    tdee = bmr * activity_mult

    # MET-based calorie burn for session
    met = {
        'Low': 4.0, 'Medium': 7.0, 'High': 10.0
    }.get(intens, 7.0)

    # Discipline type bonus
    if disc in DISCIPLINES['THROWS']:
        met *= 0.85     # shorter explosive bursts
    elif disc in DISCIPLINES['JUMPS']:
        met *= 0.90
    # TRACK stays at baseline

    session_kcal = met * w * (dur / 60)

    # Session type adjustment
    session_type_factor = {
        'Training':    1.00,
        'Competition': 1.10,
        'Recovery':    0.75,
    }.get(s_type, 1.00)

    total = tdee + session_kcal * session_type_factor
    return total

calories = df_merged.apply(compute_calories, axis=1)

# Add ±5% noise
noise_pct = np.random.normal(0, 0.03, len(df_merged))
target_calories = np.round(calories * (1 + noise_pct)).astype(int)
target_calories = np.clip(target_calories, 1200, 6000)
df_merged['target_calories'] = target_calories

# ── Step 6: Final column selection & ordering ──────────────────────────────────
FINAL_COLS = [
    'age', 'gender', 'height_cm', 'weight_kg',
    'discipline', 'session_type', 'duration_minutes',
    'intensity', 'distance_m', 'effort_count', 'target_calories'
]
df_final = df_merged[FINAL_COLS].copy()

# Cast types
df_final['age']              = df_final['age'].astype(int)
df_final['duration_minutes'] = df_final['duration_minutes'].astype(int)
df_final['distance_m']       = df_final['distance_m'].astype(int)
df_final['effort_count']     = df_final['effort_count'].astype(int)
df_final['height_cm']        = df_final['height_cm'].astype(float).round(1)
df_final['weight_kg']        = df_final['weight_kg'].astype(float).round(1)
df_final.reset_index(drop=True, inplace=True)

# ── Step 7: Save ──────────────────────────────────────────────────────────────
csv_path = 'athlete_ml_dataset.csv'
df_final.to_csv(csv_path, index=False)

# ── Step 8: Quality report ────────────────────────────────────────────────────
print("\n" + "="*55)
print("DATASET READY")
print("="*55)
print(f"Shape         : {df_final.shape}")
print(f"Saved to      : {csv_path}")
print(f"\nHead (5 rows):\n{df_final.head().to_string()}")
print(f"\ntarget_calories stats:\n{df_final['target_calories'].describe().round(1)}")

print("\nDiscipline distribution:")
print(df_final['discipline'].value_counts())

print("\nCorrelation with target_calories:")
num = df_final.copy()
num['gender_n']    = (num['gender'] == 'Male').astype(int)
num['intensity_n'] = num['intensity'].map({'Low':1,'Medium':2,'High':3})
num['stype_n']     = num['session_type'].map({'Recovery':0,'Training':1,'Competition':2})
corr_cols = ['weight_kg','height_cm','age','duration_minutes',
             'distance_m','effort_count','gender_n','intensity_n','stype_n','target_calories']
print(num[corr_cols].corr()[['target_calories']].round(3).to_string())
print("\nDone ✓")
