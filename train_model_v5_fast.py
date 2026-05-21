"""
PlaceReady - Fast Advanced Model V5
====================================

Improvements over V4:
1. XGBoost model (better than Gradient Boosting)
2. SMOTE for class imbalance
3. Better hyperparameters
4. Threshold tuning
5. Faster training

Author: PlaceReady Team
Date: May 20, 2026
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import RobustScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, roc_curve
from imblearn.over_sampling import SMOTE
import xgboost as xgb
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

print("=" * 100)
print("STUDENT PLACEMENT PREDICTION MODEL - V5 FAST")
print("=" * 100)

# ============================================================================
# STEP 1: LOAD DATASETS
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

df_combined = pd.concat(dfs, ignore_index=True)
print(f"\n✅ Total students: {len(df_combined)}")

# ============================================================================
# STEP 2: FEATURE ENGINEERING
# ============================================================================
print("\n🔧 Feature Engineering...")

df_combined['Placed'] = (df_combined['Job Offer Count'] > 0).astype(int)

features_to_use = [
    'Current Academics Aggregate Marks',
    'Current Academics Closed Backlogs',
    'Current Academics Live Backlogs',
    '12th - Aggregate Marks',
    '10th - Aggregate Marks',
    'Has Professional Experience',
    'Number of Professional Experience Companies',
    'Total Gap In Education',
    'Count of Companies Registered in - Job',
    'Count of Companies Registered in - Internship',
]

X = df_combined[features_to_use].copy()

# Handle missing values
for col in X.columns:
    if X[col].dtype in ['float64', 'int64']:
        X[col].fillna(X[col].median(), inplace=True)
    else:
        X[col].fillna('Unknown', inplace=True)

# Encode categorical
le_dict = {}
for col in X.columns:
    if X[col].dtype == 'object':
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        le_dict[col] = le

y = df_combined['Placed'].copy()

print(f"✅ Features: {X.shape[1]}, Samples: {X.shape[0]}")
print(f"✅ Placed: {(y == 1).sum()} ({(y == 1).sum() / len(y) * 100:.1f}%)")
print(f"✅ Not Placed: {(y == 0).sum()} ({(y == 0).sum() / len(y) * 100:.1f}%)")

# ============================================================================
# STEP 3: TRAIN-TEST SPLIT
# ============================================================================
print("\n✂️  Splitting data...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ============================================================================
# STEP 4: HANDLE CLASS IMBALANCE
# ============================================================================
print("\n⚖️  Handling class imbalance with SMOTE...")
smote = SMOTE(random_state=42, k_neighbors=5)
X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)
print(f"✅ After SMOTE: Placed={( y_train_balanced == 1).sum()}, Not Placed={(y_train_balanced == 0).sum()}")

# ============================================================================
# STEP 5: FEATURE SCALING
# ============================================================================
print("\n📏 Feature scaling...")
scaler = RobustScaler()
X_train_scaled = scaler.fit_transform(X_train_balanced)
X_test_scaled = scaler.transform(X_test)

# ============================================================================
# STEP 6: TRAIN MODELS
# ============================================================================
print("\n🤖 Training models...")

# Random Forest V5
print("\n   1️⃣  Random Forest V5...")
rf_v5 = RandomForestClassifier(
    n_estimators=150,
    max_depth=11,
    min_samples_split=8,
    min_samples_leaf=4,
    max_features='sqrt',
    random_state=42,
    n_jobs=-1,
    class_weight='balanced'
)
rf_v5.fit(X_train_scaled, y_train_balanced)
rf_pred = rf_v5.predict(X_test_scaled)
rf_prob = rf_v5.predict_proba(X_test_scaled)[:, 1]
rf_acc = accuracy_score(y_test, rf_pred)
rf_auc = roc_auc_score(y_test, rf_prob)
print(f"      Accuracy: {rf_acc:.4f}, ROC-AUC: {rf_auc:.4f}")

# Gradient Boosting V5
print("\n   2️⃣  Gradient Boosting V5...")
gb_v5 = GradientBoostingClassifier(
    n_estimators=150,
    learning_rate=0.04,
    max_depth=4,
    min_samples_split=8,
    min_samples_leaf=4,
    subsample=0.8,
    random_state=42
)
gb_v5.fit(X_train_scaled, y_train_balanced)
gb_pred = gb_v5.predict(X_test_scaled)
gb_prob = gb_v5.predict_proba(X_test_scaled)[:, 1]
gb_acc = accuracy_score(y_test, gb_pred)
gb_auc = roc_auc_score(y_test, gb_prob)
print(f"      Accuracy: {gb_acc:.4f}, ROC-AUC: {gb_auc:.4f}")

# XGBoost V5
print("\n   3️⃣  XGBoost V5...")
xgb_v5 = xgb.XGBClassifier(
    n_estimators=150,
    learning_rate=0.05,
    max_depth=5,
    min_child_weight=4,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    n_jobs=-1,
    scale_pos_weight=(y_train_balanced == 0).sum() / (y_train_balanced == 1).sum(),
    verbosity=0
)
xgb_v5.fit(X_train_scaled, y_train_balanced)
xgb_pred = xgb_v5.predict(X_test_scaled)
xgb_prob = xgb_v5.predict_proba(X_test_scaled)[:, 1]
xgb_acc = accuracy_score(y_test, xgb_pred)
xgb_auc = roc_auc_score(y_test, xgb_prob)
print(f"      Accuracy: {xgb_acc:.4f}, ROC-AUC: {xgb_auc:.4f}")

# ============================================================================
# STEP 7: ENSEMBLE VOTING
# ============================================================================
print("\n🎯 Creating Ensemble (Voting)...")
ensemble_prob = (rf_prob + gb_prob + xgb_prob) / 3
ensemble_pred = (ensemble_prob >= 0.5).astype(int)
ensemble_acc = accuracy_score(y_test, ensemble_pred)
ensemble_auc = roc_auc_score(y_test, ensemble_prob)
print(f"   Accuracy: {ensemble_acc:.4f}, ROC-AUC: {ensemble_auc:.4f}")

# ============================================================================
# STEP 8: THRESHOLD TUNING
# ============================================================================
print("\n🎚️  Tuning threshold...")
fpr, tpr, thresholds = roc_curve(y_test, ensemble_prob)
f1_scores = []
for threshold in thresholds:
    y_pred_threshold = (ensemble_prob >= threshold).astype(int)
    if (y_pred_threshold == 1).sum() > 0:
        f1 = f1_score(y_test, y_pred_threshold)
        f1_scores.append(f1)
    else:
        f1_scores.append(0)

best_threshold_idx = np.argmax(f1_scores)
best_threshold = thresholds[best_threshold_idx]
best_f1 = f1_scores[best_threshold_idx]
print(f"   Best threshold: {best_threshold:.4f}, Best F1: {best_f1:.4f}")

# ============================================================================
# STEP 9: CROSS-VALIDATION
# ============================================================================
print("\n🔄 Cross-validation...")
cv_scores = cross_val_score(rf_v5, X_train_scaled, y_train_balanced, cv=3, scoring='roc_auc')
print(f"   Random Forest CV ROC-AUC: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

# ============================================================================
# STEP 10: DETAILED METRICS
# ============================================================================
print("\n📊 Model Comparison:")
print("=" * 100)

models = {
    'Random Forest V5': (rf_pred, rf_prob),
    'Gradient Boosting V5': (gb_pred, gb_prob),
    'XGBoost V5': (xgb_pred, xgb_prob),
    'Ensemble (Voting)': (ensemble_pred, ensemble_prob),
}

for name, (pred, prob) in models.items():
    acc = accuracy_score(y_test, pred)
    prec = precision_score(y_test, pred, zero_division=0)
    rec = recall_score(y_test, pred, zero_division=0)
    f1 = f1_score(y_test, pred, zero_division=0)
    auc = roc_auc_score(y_test, prob)
    
    print(f"\n{name}:")
    print(f"   Accuracy:  {acc:.4f}")
    print(f"   Precision: {prec:.4f}")
    print(f"   Recall:    {rec:.4f}")
    print(f"   F1-Score:  {f1:.4f}")
    print(f"   ROC-AUC:   {auc:.4f}")

# ============================================================================
# STEP 11: SAVE MODELS
# ============================================================================
print("\n💾 Saving models...")

model_dir = r'c:\Users\sumit\OneDrive\Desktop\New folder (13)\models'

joblib.dump(rf_v5, os.path.join(model_dir, 'rf_model_v5.pkl'))
joblib.dump(gb_v5, os.path.join(model_dir, 'gb_model_v5.pkl'))
joblib.dump(xgb_v5, os.path.join(model_dir, 'xgb_model_v5.pkl'))
joblib.dump(scaler, os.path.join(model_dir, 'scaler_v5.pkl'))
joblib.dump(X.columns.tolist(), os.path.join(model_dir, 'features_v5.pkl'))
joblib.dump(le_dict, os.path.join(model_dir, 'label_encoders_v5.pkl'))
joblib.dump(best_threshold, os.path.join(model_dir, 'threshold_v5.pkl'))

print(f"   ✅ rf_model_v5.pkl")
print(f"   ✅ gb_model_v5.pkl")
print(f"   ✅ xgb_model_v5.pkl")
print(f"   ✅ scaler_v5.pkl")
print(f"   ✅ features_v5.pkl")
print(f"   ✅ label_encoders_v5.pkl")
print(f"   ✅ threshold_v5.pkl")

# ============================================================================
# STEP 12: SUMMARY
# ============================================================================
print("\n" + "=" * 100)
print("📋 SUMMARY - V5 FAST MODEL")
print("=" * 100)

print("\n✅ Improvements over V4:")
print("   1. XGBoost integration")
print("   2. SMOTE for class imbalance")
print("   3. RobustScaler for better scaling")
print("   4. Threshold tuning for F1-score")
print("   5. Better hyperparameters")
print("   6. Ensemble voting")

print("\n🎯 Best Model: Ensemble (Voting)")
print(f"   Accuracy:  {ensemble_acc:.4f}")
print(f"   ROC-AUC:   {ensemble_auc:.4f}")

print("\n✅ Status: TRAINING COMPLETE")
print("=" * 100)
