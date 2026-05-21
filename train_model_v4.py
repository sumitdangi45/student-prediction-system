import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("STUDENT PLACEMENT PREDICTION MODEL - V4 (ENHANCED FEATURES)")
print("=" * 80)

# ============================================================================
# STEP 1: LOAD AND COMBINE ALL DATASETS
# ============================================================================
print("\n📂 Loading datasets...")

dataset_dir = r'c:\Users\sumit\OneDrive\Desktop\New folder (13)\dataset'
files = [
    'Students-List-15-05-2026-07-08-24-0KBlEw.xlsx',
    'Students-List-15-05-2026-08-14-30-puVIEw.xlsx',
    'Students-List-15-05-2026-08-54-10-zBSlEw.xlsx',
    'Students-List-15-05-2026-09-00-36-RoOXEw.xlsx'
]

dfs = []
for file in files:
    file_path = os.path.join(dataset_dir, file)
    try:
        df = pd.read_excel(file_path)
        dfs.append(df)
        print(f"   ✅ {file}: {len(df)} students")
    except Exception as e:
        print(f"   ❌ {file}: {e}")

# Combine all dataframes
df_combined = pd.concat(dfs, ignore_index=True)
print(f"\n✅ Total students loaded: {len(df_combined)}")
print(f"✅ Total columns: {len(df_combined.columns)}")

# ============================================================================
# STEP 2: FEATURE ENGINEERING (V4 - ENHANCED)
# ============================================================================
print("\n🔧 Feature Engineering (V4 - Enhanced)...")

# Create target variable: Placement Status (1 = Placed, 0 = Not Placed)
df_combined['Placed'] = (df_combined['Job Offer Count'] > 0).astype(int)

print(f"   Placed: {(df_combined['Placed'] == 1).sum()}")
print(f"   Not Placed: {(df_combined['Placed'] == 0).sum()}")

# Select relevant features - V4 ENHANCED
features_to_use = [
    'Current Academics Aggregate Marks',  # CGPA
    'Current Academics Closed Backlogs',  # Closed backlogs
    'Current Academics Live Backlogs',    # Live backlogs
    '12th - Aggregate Marks',
    '10th - Aggregate Marks',
    'Has Professional Experience',
    'Number of Professional Experience Companies',
    'Count of Companies Registered in - Job',
    'Count of Companies Registered in - Internship',
    'Gender',
]

# Create feature dataframe
X = df_combined[features_to_use].copy()

# Handle missing values
print("\n📊 Handling missing values...")
for col in X.columns:
    if X[col].dtype in ['float64', 'int64']:
        X[col].fillna(X[col].median(), inplace=True)
    else:
        X[col].fillna('Unknown', inplace=True)

# Encode categorical variables
print("🔤 Encoding categorical variables...")
le_dict = {}
for col in X.columns:
    if X[col].dtype == 'object':
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        le_dict[col] = le

# Target variable
y = df_combined['Placed'].copy()

print(f"\n✅ Features prepared: {X.shape[1]}")
print(f"✅ Samples: {X.shape[0]}")
print(f"✅ Target distribution:")
print(f"   - Placed (1): {(y == 1).sum()} ({(y == 1).sum() / len(y) * 100:.1f}%)")
print(f"   - Not Placed (0): {(y == 0).sum()} ({(y == 0).sum() / len(y) * 100:.1f}%)")

# ============================================================================
# STEP 3: TRAIN-TEST SPLIT
# ============================================================================
print("\n✂️  Splitting data...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"   Training set: {X_train.shape[0]} samples")
print(f"   Test set: {X_test.shape[0]} samples")

# ============================================================================
# STEP 4: FEATURE SCALING
# ============================================================================
print("\n📈 Scaling features...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ============================================================================
# STEP 5: MODEL TRAINING WITH REGULARIZATION
# ============================================================================
print("\n🤖 Training models with regularization...")

# Model 1: Random Forest (with regularization to prevent overfitting)
print("\n   Training Random Forest...")
rf_model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    min_samples_split=10,
    min_samples_leaf=5,
    max_features='sqrt',
    random_state=42,
    n_jobs=-1
)
rf_model.fit(X_train_scaled, y_train)

# Model 2: Gradient Boosting (with regularization)
print("   Training Gradient Boosting...")
gb_model = GradientBoostingClassifier(
    n_estimators=100,
    learning_rate=0.05,
    max_depth=3,
    min_samples_split=10,
    min_samples_leaf=5,
    subsample=0.8,
    random_state=42
)
gb_model.fit(X_train_scaled, y_train)

# ============================================================================
# STEP 6: OVERFITTING CHECK
# ============================================================================
print("\n🔍 OVERFITTING ANALYSIS:")

# Random Forest
rf_train_pred = rf_model.predict(X_train_scaled)
rf_test_pred = rf_model.predict(X_test_scaled)
rf_train_acc = accuracy_score(y_train, rf_train_pred)
rf_test_acc = accuracy_score(y_test, rf_test_pred)
rf_overfit = rf_train_acc - rf_test_acc

print(f"\n🌲 RANDOM FOREST:")
print(f"   Train Accuracy: {rf_train_acc:.4f}")
print(f"   Test Accuracy:  {rf_test_acc:.4f}")
print(f"   Overfitting Gap: {rf_overfit:.4f}")
if rf_overfit > 0.1:
    print(f"   ⚠️  WARNING: Possible overfitting detected!")
else:
    print(f"   ✅ Good generalization!")

# Gradient Boosting
gb_train_pred = gb_model.predict(X_train_scaled)
gb_test_pred = gb_model.predict(X_test_scaled)
gb_train_acc = accuracy_score(y_train, gb_train_pred)
gb_test_acc = accuracy_score(y_test, gb_test_pred)
gb_overfit = gb_train_acc - gb_test_acc

print(f"\n📈 GRADIENT BOOSTING:")
print(f"   Train Accuracy: {gb_train_acc:.4f}")
print(f"   Test Accuracy:  {gb_test_acc:.4f}")
print(f"   Overfitting Gap: {gb_overfit:.4f}")
if gb_overfit > 0.1:
    print(f"   ⚠️  WARNING: Possible overfitting detected!")
else:
    print(f"   ✅ Good generalization!")

# ============================================================================
# STEP 7: DETAILED MODEL EVALUATION
# ============================================================================
print("\n📊 DETAILED MODEL EVALUATION:")

# Random Forest Predictions
rf_pred_proba = rf_model.predict_proba(X_test_scaled)[:, 1]

print("\n🌲 RANDOM FOREST TEST SET RESULTS:")
print(f"   Accuracy:  {accuracy_score(y_test, rf_test_pred):.4f}")
print(f"   Precision: {precision_score(y_test, rf_test_pred):.4f}")
print(f"   Recall:    {recall_score(y_test, rf_test_pred):.4f}")
print(f"   F1-Score:  {f1_score(y_test, rf_test_pred):.4f}")
print(f"   ROC-AUC:   {roc_auc_score(y_test, rf_pred_proba):.4f}")

# Gradient Boosting Predictions
gb_pred_proba = gb_model.predict_proba(X_test_scaled)[:, 1]

print("\n📈 GRADIENT BOOSTING TEST SET RESULTS:")
print(f"   Accuracy:  {accuracy_score(y_test, gb_test_pred):.4f}")
print(f"   Precision: {precision_score(y_test, gb_test_pred):.4f}")
print(f"   Recall:    {recall_score(y_test, gb_test_pred):.4f}")
print(f"   F1-Score:  {f1_score(y_test, gb_test_pred):.4f}")
print(f"   ROC-AUC:   {roc_auc_score(y_test, gb_pred_proba):.4f}")

# ============================================================================
# STEP 8: CROSS-VALIDATION
# ============================================================================
print("\n🔄 CROSS-VALIDATION (5-Fold):")

rf_cv_scores = cross_val_score(rf_model, X_train_scaled, y_train, cv=5, scoring='accuracy')
gb_cv_scores = cross_val_score(gb_model, X_train_scaled, y_train, cv=5, scoring='accuracy')

print(f"\n🌲 Random Forest CV Scores: {rf_cv_scores}")
print(f"   Mean: {rf_cv_scores.mean():.4f} (+/- {rf_cv_scores.std():.4f})")

print(f"\n📈 Gradient Boosting CV Scores: {gb_cv_scores}")
print(f"   Mean: {gb_cv_scores.mean():.4f} (+/- {gb_cv_scores.std():.4f})")

# ============================================================================
# STEP 9: FEATURE IMPORTANCE
# ============================================================================
print("\n⭐ FEATURE IMPORTANCE (Random Forest V4):")
feature_importance = pd.DataFrame({
    'Feature': features_to_use,
    'Importance': rf_model.feature_importances_
}).sort_values('Importance', ascending=False)

for idx, row in feature_importance.iterrows():
    print(f"   {row['Feature']}: {row['Importance']:.4f}")

# ============================================================================
# STEP 10: SAVE MODELS
# ============================================================================
print("\n💾 Saving V4 models...")

model_dir = r'c:\Users\sumit\OneDrive\Desktop\New folder (13)\models'
os.makedirs(model_dir, exist_ok=True)

joblib.dump(rf_model, os.path.join(model_dir, 'rf_model_v4.pkl'))
joblib.dump(gb_model, os.path.join(model_dir, 'gb_model_v4.pkl'))
joblib.dump(scaler, os.path.join(model_dir, 'scaler_v4.pkl'))
joblib.dump(le_dict, os.path.join(model_dir, 'label_encoders_v4.pkl'))
joblib.dump(features_to_use, os.path.join(model_dir, 'features_v4.pkl'))

print(f"   ✅ Models saved to: {model_dir}")

print("\n" + "=" * 80)
print("✅ V4 MODEL TRAINING COMPLETE!")
print("=" * 80)
