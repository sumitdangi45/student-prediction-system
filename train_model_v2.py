import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from imblearn.over_sampling import SMOTE
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("STUDENT PLACEMENT PREDICTION MODEL V2 - IMPROVED")
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

df_combined = pd.concat(dfs, ignore_index=True)
print(f"\n✅ Total students: {len(df_combined)}")

# ============================================================================
# STEP 2: ADVANCED FEATURE ENGINEERING
# ============================================================================
print("\n🔧 Advanced Feature Engineering...")

# Target: Placement Status
df_combined['Placed'] = (df_combined['Job Offer Count'] > 0).astype(int)

# Create more features
df_combined['CGPA'] = df_combined['Current Academics Aggregate Marks']
df_combined['12th_Marks'] = df_combined['12th - Aggregate Marks']
df_combined['10th_Marks'] = df_combined['10th - Aggregate Marks']
df_combined['Total_Backlogs'] = (
    df_combined['Current Academics Closed Backlogs'].fillna(0) + 
    df_combined['Current Academics Live Backlogs'].fillna(0)
)
df_combined['Has_Experience'] = (df_combined['Has Professional Experience'] == 'Yes').astype(int)
df_combined['Num_Companies'] = df_combined['Number of Professional Experience Companies'].fillna(0)
df_combined['Has_Internship'] = df_combined['Internship Experience - Organization Name (Industry - Stipend (INR Per Month) - Start date to End date[Duration]) - Mentor Name (Designation - Phone - Email) - Academic Guide Name 1'].notna().astype(int)

# Skills count (approximate)
df_combined['Has_Skills'] = df_combined['Key Skills'].notna().astype(int)
df_combined['Has_Projects'] = df_combined['Projects Name'].notna().astype(int)
df_combined['Has_Certifications'] = df_combined['Assessments/Certification (Name - Provider - Aggregate Marks)'].notna().astype(int)

# Academic performance trend
df_combined['Sem1_Marks'] = df_combined['Year/Semester 1 - Aggregate Marks']
df_combined['Sem8_Marks'] = df_combined['Year/Semester 8 - Aggregate Marks']
df_combined['Academic_Trend'] = (df_combined['Sem8_Marks'] - df_combined['Sem1_Marks']).fillna(0)

# Gender encoding
df_combined['Is_Female'] = (df_combined['Gender'] == 'Female').astype(int)

features_to_use = [
    'CGPA',
    '12th_Marks',
    '10th_Marks',
    'Total_Backlogs',
    'Has_Experience',
    'Num_Companies',
    'Has_Internship',
    'Has_Skills',
    'Has_Projects',
    'Has_Certifications',
    'Academic_Trend',
    'Is_Female'
]

X = df_combined[features_to_use].copy()

# Handle missing values
print("📊 Handling missing values...")
for col in X.columns:
    if X[col].dtype in ['float64', 'int64']:
        X[col].fillna(X[col].median(), inplace=True)
    else:
        X[col].fillna(0, inplace=True)

y = df_combined['Placed'].copy()

print(f"\n✅ Features: {X.shape[1]}")
print(f"✅ Samples: {X.shape[0]}")
print(f"✅ Class Distribution:")
print(f"   - Placed (1): {(y == 1).sum()} ({(y == 1).sum() / len(y) * 100:.1f}%)")
print(f"   - Not Placed (0): {(y == 0).sum()} ({(y == 0).sum() / len(y) * 100:.1f}%)")

# ============================================================================
# STEP 3: TRAIN-TEST SPLIT
# ============================================================================
print("\n✂️  Splitting data...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ============================================================================
# STEP 4: HANDLE CLASS IMBALANCE WITH SMOTE
# ============================================================================
print("\n⚖️  Applying SMOTE for class balancing...")
smote = SMOTE(random_state=42, k_neighbors=5)
X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)

print(f"   After SMOTE:")
print(f"   - Placed (1): {(y_train_balanced == 1).sum()}")
print(f"   - Not Placed (0): {(y_train_balanced == 0).sum()}")

# ============================================================================
# STEP 5: FEATURE SCALING
# ============================================================================
print("\n📈 Scaling features...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_balanced)
X_test_scaled = scaler.transform(X_test)

# ============================================================================
# STEP 6: MODEL TRAINING WITH CLASS WEIGHTS
# ============================================================================
print("\n🤖 Training improved models...")

# Calculate class weights
class_weights = compute_class_weight('balanced', classes=np.unique(y_train), y=y_train)
class_weight_dict = {0: class_weights[0], 1: class_weights[1]}

print(f"   Class weights: {class_weight_dict}")

# Random Forest with class weights
print("\n   Training Random Forest...")
rf_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=20,
    min_samples_split=3,
    min_samples_leaf=1,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)
rf_model.fit(X_train_scaled, y_train_balanced)

# Gradient Boosting
print("   Training Gradient Boosting...")
gb_model = GradientBoostingClassifier(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=7,
    min_samples_split=3,
    min_samples_leaf=1,
    subsample=0.8,
    random_state=42
)
gb_model.fit(X_train_scaled, y_train_balanced)

# ============================================================================
# STEP 7: MODEL EVALUATION
# ============================================================================
print("\n📊 Model Evaluation...")

# Random Forest
rf_pred = rf_model.predict(X_test_scaled)
rf_pred_proba = rf_model.predict_proba(X_test_scaled)[:, 1]

# Gradient Boosting
gb_pred = gb_model.predict(X_test_scaled)
gb_pred_proba = gb_model.predict_proba(X_test_scaled)[:, 1]

print("\n🌲 RANDOM FOREST RESULTS:")
print(f"   Accuracy:  {accuracy_score(y_test, rf_pred):.4f}")
print(f"   Precision: {precision_score(y_test, rf_pred, zero_division=0):.4f}")
print(f"   Recall:    {recall_score(y_test, rf_pred, zero_division=0):.4f}")
print(f"   F1-Score:  {f1_score(y_test, rf_pred, zero_division=0):.4f}")
print(f"   ROC-AUC:   {roc_auc_score(y_test, rf_pred_proba):.4f}")

print("\n📈 GRADIENT BOOSTING RESULTS:")
print(f"   Accuracy:  {accuracy_score(y_test, gb_pred):.4f}")
print(f"   Precision: {precision_score(y_test, gb_pred, zero_division=0):.4f}")
print(f"   Recall:    {recall_score(y_test, gb_pred, zero_division=0):.4f}")
print(f"   F1-Score:  {f1_score(y_test, gb_pred, zero_division=0):.4f}")
print(f"   ROC-AUC:   {roc_auc_score(y_test, gb_pred_proba):.4f}")

# Confusion Matrix
print("\n🔍 CONFUSION MATRIX (Random Forest):")
cm = confusion_matrix(y_test, rf_pred)
print(f"   True Negatives:  {cm[0][0]}")
print(f"   False Positives: {cm[0][1]}")
print(f"   False Negatives: {cm[1][0]}")
print(f"   True Positives:  {cm[1][1]}")

# ============================================================================
# STEP 8: FEATURE IMPORTANCE
# ============================================================================
print("\n⭐ FEATURE IMPORTANCE (Random Forest):")
feature_importance = pd.DataFrame({
    'Feature': features_to_use,
    'Importance': rf_model.feature_importances_
}).sort_values('Importance', ascending=False)

for idx, row in feature_importance.iterrows():
    print(f"   {row['Feature']}: {row['Importance']:.4f}")

# ============================================================================
# STEP 9: SAVE MODELS
# ============================================================================
print("\n💾 Saving models...")

model_dir = r'c:\Users\sumit\OneDrive\Desktop\New folder (13)\models'
os.makedirs(model_dir, exist_ok=True)

joblib.dump(rf_model, os.path.join(model_dir, 'rf_model_v2.pkl'))
joblib.dump(gb_model, os.path.join(model_dir, 'gb_model_v2.pkl'))
joblib.dump(scaler, os.path.join(model_dir, 'scaler_v2.pkl'))
joblib.dump(features_to_use, os.path.join(model_dir, 'features_v2.pkl'))

print(f"   ✅ Models saved to: {model_dir}")

# ============================================================================
# STEP 10: SAMPLE PREDICTIONS
# ============================================================================
print("\n🎯 SAMPLE PREDICTIONS:")
print("\nTop 10 students most likely to be placed:")
top_indices = np.argsort(rf_pred_proba)[-10:][::-1]
for i, idx in enumerate(top_indices, 1):
    print(f"   {i}. Probability: {rf_pred_proba[idx]:.2%}")

print("\nTop 10 students least likely to be placed:")
bottom_indices = np.argsort(rf_pred_proba)[:10]
for i, idx in enumerate(bottom_indices, 1):
    print(f"   {i}. Probability: {rf_pred_proba[idx]:.2%}")

print("\n" + "=" * 80)
print("✅ MODEL V2 TRAINING COMPLETE!")
print("=" * 80)
