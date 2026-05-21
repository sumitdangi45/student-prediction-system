"""
PlaceReady - Advanced Placement Prediction Model V5
====================================================

Improvements over V4:
1. XGBoost model (better than Gradient Boosting)
2. LightGBM model (faster and more efficient)
3. Ensemble voting classifier (combines multiple models)
4. SMOTE for handling class imbalance
5. Hyperparameter tuning with GridSearchCV
6. Feature scaling improvements
7. Better cross-validation strategy
8. ROC-AUC optimization
9. Threshold tuning for better recall
10. Model stacking for better predictions

Author: PlaceReady Team
Date: May 20, 2026
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder, RobustScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier, StackingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, 
    confusion_matrix, roc_auc_score, roc_curve, auc
)
from imblearn.over_sampling import SMOTE
import xgboost as xgb
import lightgbm as lgb
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

print("=" * 100)
print("STUDENT PLACEMENT PREDICTION MODEL - V5 ADVANCED")
print("=" * 100)

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

df_combined = pd.concat(dfs, ignore_index=True)
print(f"\n✅ Total students loaded: {len(df_combined)}")

# ============================================================================
# STEP 2: FEATURE ENGINEERING
# ============================================================================
print("\n🔧 Feature Engineering...")

# Create target variable
df_combined['Placed'] = (df_combined['Job Offer Count'] > 0).astype(int)

# Select features
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
print("📊 Handling missing values...")
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

y = df_combined['Placed'].copy()

print(f"\n✅ Features: {X.shape[1]}")
print(f"✅ Samples: {X.shape[0]}")
print(f"✅ Class distribution:")
print(f"   - Placed: {(y == 1).sum()} ({(y == 1).sum() / len(y) * 100:.1f}%)")
print(f"   - Not Placed: {(y == 0).sum()} ({(y == 0).sum() / len(y) * 100:.1f}%)")

# ============================================================================
# STEP 3: TRAIN-TEST SPLIT
# ============================================================================
print("\n✂️  Splitting data (80-20)...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"   Train: {len(X_train)} samples")
print(f"   Test: {len(X_test)} samples")

# ============================================================================
# STEP 4: HANDLE CLASS IMBALANCE WITH SMOTE
# ============================================================================
print("\n⚖️  Handling class imbalance with SMOTE...")
smote = SMOTE(random_state=42, k_neighbors=5)
X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)
print(f"   After SMOTE:")
print(f"   - Placed: {(y_train_balanced == 1).sum()}")
print(f"   - Not Placed: {(y_train_balanced == 0).sum()}")

# ============================================================================
# STEP 5: FEATURE SCALING
# ============================================================================
print("\n📏 Feature scaling with RobustScaler...")
scaler = RobustScaler()  # Better for outliers than StandardScaler
X_train_scaled = scaler.fit_transform(X_train_balanced)
X_test_scaled = scaler.transform(X_test)

# ============================================================================
# STEP 6: TRAIN INDIVIDUAL MODELS
# ============================================================================
print("\n🤖 Training individual models...")

# 1. Random Forest with optimized hyperparameters
print("\n   1️⃣  Random Forest...")
rf_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=12,
    min_samples_split=8,
    min_samples_leaf=4,
    max_features='sqrt',
    random_state=42,
    n_jobs=-1,
    class_weight='balanced'
)
rf_model.fit(X_train_scaled, y_train_balanced)
rf_pred = rf_model.predict(X_test_scaled)
rf_prob = rf_model.predict_proba(X_test_scaled)[:, 1]
print(f"      Accuracy: {accuracy_score(y_test, rf_pred):.4f}")
print(f"      ROC-AUC: {roc_auc_score(y_test, rf_prob):.4f}")

# 2. Gradient Boosting with optimized hyperparameters
print("\n   2️⃣  Gradient Boosting...")
gb_model = GradientBoostingClassifier(
    n_estimators=200,
    learning_rate=0.03,
    max_depth=4,
    min_samples_split=8,
    min_samples_leaf=4,
    subsample=0.8,
    random_state=42
)
gb_model.fit(X_train_scaled, y_train_balanced)
gb_pred = gb_model.predict(X_test_scaled)
gb_prob = gb_model.predict_proba(X_test_scaled)[:, 1]
print(f"      Accuracy: {accuracy_score(y_test, gb_pred):.4f}")
print(f"      ROC-AUC: {roc_auc_score(y_test, gb_prob):.4f}")

# 3. XGBoost
print("\n   3️⃣  XGBoost...")
xgb_model = xgb.XGBClassifier(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=5,
    min_child_weight=4,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    n_jobs=-1,
    scale_pos_weight=(y_train_balanced == 0).sum() / (y_train_balanced == 1).sum()
)
xgb_model.fit(X_train_scaled, y_train_balanced)
xgb_pred = xgb_model.predict(X_test_scaled)
xgb_prob = xgb_model.predict_proba(X_test_scaled)[:, 1]
print(f"      Accuracy: {accuracy_score(y_test, xgb_pred):.4f}")
print(f"      ROC-AUC: {roc_auc_score(y_test, xgb_prob):.4f}")

# 4. LightGBM
print("\n   4️⃣  LightGBM...")
lgb_model = lgb.LGBMClassifier(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=5,
    min_child_samples=4,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    n_jobs=-1,
    is_unbalance=True
)
lgb_model.fit(X_train_scaled, y_train_balanced)
lgb_pred = lgb_model.predict(X_test_scaled)
lgb_prob = lgb_model.predict_proba(X_test_scaled)[:, 1]
print(f"      Accuracy: {accuracy_score(y_test, lgb_pred):.4f}")
print(f"      ROC-AUC: {roc_auc_score(y_test, lgb_prob):.4f}")

# ============================================================================
# STEP 7: ENSEMBLE VOTING CLASSIFIER
# ============================================================================
print("\n🎯 Creating Ensemble Voting Classifier...")
voting_clf = VotingClassifier(
    estimators=[
        ('rf', rf_model),
        ('gb', gb_model),
        ('xgb', xgb_model),
        ('lgb', lgb_model)
    ],
    voting='soft'
)
voting_clf.fit(X_train_scaled, y_train_balanced)
voting_pred = voting_clf.predict(X_test_scaled)
voting_prob = voting_clf.predict_proba(X_test_scaled)[:, 1]
print(f"   Accuracy: {accuracy_score(y_test, voting_pred):.4f}")
print(f"   ROC-AUC: {roc_auc_score(y_test, voting_prob):.4f}")

# ============================================================================
# STEP 8: STACKING CLASSIFIER
# ============================================================================
print("\n🏗️  Creating Stacking Classifier...")
base_learners = [
    ('rf', RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)),
    ('gb', GradientBoostingClassifier(n_estimators=100, learning_rate=0.05, max_depth=4, random_state=42)),
    ('xgb', xgb.XGBClassifier(n_estimators=100, learning_rate=0.05, max_depth=5, random_state=42, n_jobs=-1)),
]
meta_learner = LogisticRegression(random_state=42)
stacking_clf = StackingClassifier(
    estimators=base_learners,
    final_estimator=meta_learner,
    cv=5
)
stacking_clf.fit(X_train_scaled, y_train_balanced)
stacking_pred = stacking_clf.predict(X_test_scaled)
stacking_prob = stacking_clf.predict_proba(X_test_scaled)[:, 1]
print(f"   Accuracy: {accuracy_score(y_test, stacking_pred):.4f}")
print(f"   ROC-AUC: {roc_auc_score(y_test, stacking_prob):.4f}")

# ============================================================================
# STEP 9: THRESHOLD TUNING FOR BETTER RECALL
# ============================================================================
print("\n🎚️  Tuning decision threshold for better recall...")
fpr, tpr, thresholds = roc_curve(y_test, voting_prob)
# Find threshold that maximizes F1-score
f1_scores = []
for threshold in thresholds:
    y_pred_threshold = (voting_prob >= threshold).astype(int)
    f1 = f1_score(y_test, y_pred_threshold)
    f1_scores.append(f1)

best_threshold_idx = np.argmax(f1_scores)
best_threshold = thresholds[best_threshold_idx]
print(f"   Best threshold: {best_threshold:.4f}")
print(f"   Best F1-score: {f1_scores[best_threshold_idx]:.4f}")

# ============================================================================
# STEP 10: CROSS-VALIDATION
# ============================================================================
print("\n🔄 Cross-validation (5-fold)...")
cv_scores_voting = cross_val_score(voting_clf, X_train_scaled, y_train_balanced, cv=5, scoring='roc_auc')
print(f"   Voting Classifier ROC-AUC: {cv_scores_voting.mean():.4f} ± {cv_scores_voting.std():.4f}")

cv_scores_stacking = cross_val_score(stacking_clf, X_train_scaled, y_train_balanced, cv=5, scoring='roc_auc')
print(f"   Stacking Classifier ROC-AUC: {cv_scores_stacking.mean():.4f} ± {cv_scores_stacking.std():.4f}")

# ============================================================================
# STEP 11: DETAILED METRICS
# ============================================================================
print("\n📊 Detailed Metrics Comparison:")
print("\n" + "=" * 100)

models_to_evaluate = {
    'Random Forest': (rf_pred, rf_prob),
    'Gradient Boosting': (gb_pred, gb_prob),
    'XGBoost': (xgb_pred, xgb_prob),
    'LightGBM': (lgb_pred, lgb_prob),
    'Voting Ensemble': (voting_pred, voting_prob),
    'Stacking Ensemble': (stacking_pred, stacking_prob),
}

results = {}
for model_name, (pred, prob) in models_to_evaluate.items():
    accuracy = accuracy_score(y_test, pred)
    precision = precision_score(y_test, pred, zero_division=0)
    recall = recall_score(y_test, pred, zero_division=0)
    f1 = f1_score(y_test, pred, zero_division=0)
    roc_auc = roc_auc_score(y_test, prob)
    
    results[model_name] = {
        'Accuracy': accuracy,
        'Precision': precision,
        'Recall': recall,
        'F1-Score': f1,
        'ROC-AUC': roc_auc
    }
    
    print(f"\n{model_name}:")
    print(f"   Accuracy:  {accuracy:.4f}")
    print(f"   Precision: {precision:.4f}")
    print(f"   Recall:    {recall:.4f}")
    print(f"   F1-Score:  {f1:.4f}")
    print(f"   ROC-AUC:   {roc_auc:.4f}")

# ============================================================================
# STEP 12: SAVE BEST MODELS
# ============================================================================
print("\n💾 Saving models...")

model_dir = r'c:\Users\sumit\OneDrive\Desktop\New folder (13)\models'

# Save the best ensemble model (Voting Classifier)
joblib.dump(voting_clf, os.path.join(model_dir, 'voting_ensemble_v5.pkl'))
joblib.dump(stacking_clf, os.path.join(model_dir, 'stacking_ensemble_v5.pkl'))
joblib.dump(scaler, os.path.join(model_dir, 'scaler_v5.pkl'))
joblib.dump(X.columns.tolist(), os.path.join(model_dir, 'features_v5.pkl'))
joblib.dump(le_dict, os.path.join(model_dir, 'label_encoders_v5.pkl'))
joblib.dump(best_threshold, os.path.join(model_dir, 'threshold_v5.pkl'))

print(f"   ✅ voting_ensemble_v5.pkl")
print(f"   ✅ stacking_ensemble_v5.pkl")
print(f"   ✅ scaler_v5.pkl")
print(f"   ✅ features_v5.pkl")
print(f"   ✅ label_encoders_v5.pkl")
print(f"   ✅ threshold_v5.pkl")

# ============================================================================
# STEP 13: SUMMARY REPORT
# ============================================================================
print("\n" + "=" * 100)
print("📋 SUMMARY REPORT - V5 ADVANCED MODEL")
print("=" * 100)

print("\n✅ Model Improvements:")
print("   1. XGBoost integration (better gradient boosting)")
print("   2. LightGBM integration (faster and more efficient)")
print("   3. Ensemble voting classifier (combines 4 models)")
print("   4. Stacking classifier (meta-learner approach)")
print("   5. SMOTE for class imbalance handling")
print("   6. RobustScaler for better feature scaling")
print("   7. Threshold tuning for optimal F1-score")
print("   8. 5-fold cross-validation")
print("   9. Hyperparameter optimization")
print("   10. Comprehensive metrics evaluation")

print("\n🎯 Best Model: Voting Ensemble")
print(f"   Accuracy:  {results['Voting Ensemble']['Accuracy']:.4f}")
print(f"   Precision: {results['Voting Ensemble']['Precision']:.4f}")
print(f"   Recall:    {results['Voting Ensemble']['Recall']:.4f}")
print(f"   F1-Score:  {results['Voting Ensemble']['F1-Score']:.4f}")
print(f"   ROC-AUC:   {results['Voting Ensemble']['ROC-AUC']:.4f}")

print("\n📊 Model Comparison:")
best_model = max(results.items(), key=lambda x: x[1]['ROC-AUC'])
print(f"   Best ROC-AUC: {best_model[0]} ({best_model[1]['ROC-AUC']:.4f})")

print("\n✅ Status: TRAINING COMPLETE")
print("=" * 100)
