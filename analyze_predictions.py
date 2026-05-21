#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyze student predictions with detailed visualizations
"""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import numpy as np

load_dotenv()

# MongoDB connection
MONGODB_URI = os.getenv('MONGODB_URI')
mongo_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
db = mongo_client['placeready']

print("=" * 80)
print("[ANALYSIS] Student Predictions Analysis")
print("=" * 80)

# Get all predictions
predictions = list(db.predictions.find({}).sort('timestamp', -1))
print(f"\n[INFO] Total predictions: {len(predictions)}")

# Create DataFrame
data = []
for pred in predictions:
    features = pred.get('features', {})
    data.append({
        'Name': features.get('name', 'N/A'),
        'Email': features.get('email', 'N/A'),
        'Tier': pred.get('tier', 'Unknown'),
        'Probability': pred.get('probability', 0),
        'CGPA': features.get('Current Academics Aggregate Marks', 0),
        'Aptitude': features.get('Aptitude Test Score', 0),
        'Communication': features.get('Communication Skills', 0),
        'Technical': features.get('Technical Skills', 0),
        'Internship': features.get('Internship Experience', 0),
        'Projects': features.get('Projects Completed', 0),
    })

df = pd.DataFrame(data)

print(f"\n[DATA] DataFrame created with {len(df)} records")
print(f"\n[TIERS] Distribution:")
print(df['Tier'].value_counts())

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 12)

# Create figure with subplots
fig = plt.figure(figsize=(20, 14))

# 1. Tier Distribution - Pie Chart
ax1 = plt.subplot(3, 3, 1)
tier_counts = df['Tier'].value_counts()
colors = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c']
ax1.pie(tier_counts.values, labels=tier_counts.index, autopct='%1.1f%%', 
        colors=colors, startangle=90, textprops={'fontsize': 10, 'weight': 'bold'})
ax1.set_title('Tier Distribution (Pie Chart)', fontsize=12, weight='bold')

# 2. Tier Distribution - Bar Chart
ax2 = plt.subplot(3, 3, 2)
tier_counts.plot(kind='bar', ax=ax2, color=colors)
ax2.set_title('Tier Distribution (Bar Chart)', fontsize=12, weight='bold')
ax2.set_xlabel('Tier', fontsize=10)
ax2.set_ylabel('Count', fontsize=10)
ax2.tick_params(axis='x', rotation=45)
for i, v in enumerate(tier_counts.values):
    ax2.text(i, v + 0.1, str(v), ha='center', va='bottom', weight='bold')

# 3. Probability Distribution by Tier
ax3 = plt.subplot(3, 3, 3)
sns.boxplot(data=df, x='Tier', y='Probability', ax=ax3, palette='Set2')
ax3.set_title('Probability Distribution by Tier', fontsize=12, weight='bold')
ax3.set_xlabel('Tier', fontsize=10)
ax3.set_ylabel('Probability', fontsize=10)

# 4. CGPA vs Probability
ax4 = plt.subplot(3, 3, 4)
scatter = ax4.scatter(df['CGPA'], df['Probability'], 
                     c=pd.Categorical(df['Tier']).codes, 
                     cmap='viridis', s=100, alpha=0.6, edgecolors='black')
ax4.set_title('CGPA vs Probability', fontsize=12, weight='bold')
ax4.set_xlabel('CGPA', fontsize=10)
ax4.set_ylabel('Probability', fontsize=10)
plt.colorbar(scatter, ax=ax4, label='Tier')

# 5. Aptitude Score Distribution
ax5 = plt.subplot(3, 3, 5)
sns.histplot(data=df, x='Aptitude', hue='Tier', ax=ax5, palette='Set2')
ax5.set_title('Aptitude Score Distribution by Tier', fontsize=12, weight='bold')
ax5.set_xlabel('Aptitude Score', fontsize=10)
ax5.set_ylabel('Count', fontsize=10)

# 6. Communication Skills Distribution
ax6 = plt.subplot(3, 3, 6)
sns.violinplot(data=df, x='Tier', y='Communication', ax=ax6, palette='Set2')
ax6.set_title('Communication Skills by Tier', fontsize=12, weight='bold')
ax6.set_xlabel('Tier', fontsize=10)
ax6.set_ylabel('Communication Score', fontsize=10)

# 7. Technical Skills Distribution
ax7 = plt.subplot(3, 3, 7)
sns.violinplot(data=df, x='Tier', y='Technical', ax=ax7, palette='Set2')
ax7.set_title('Technical Skills by Tier', fontsize=12, weight='bold')
ax7.set_xlabel('Tier', fontsize=10)
ax7.set_ylabel('Technical Score', fontsize=10)

# 8. Internship Experience
ax8 = plt.subplot(3, 3, 8)
sns.barplot(data=df, x='Tier', y='Internship', ax=ax8, palette='Set2', ci=95)
ax8.set_title('Average Internship Experience by Tier', fontsize=12, weight='bold')
ax8.set_xlabel('Tier', fontsize=10)
ax8.set_ylabel('Internship Count', fontsize=10)

# 9. Projects Completed
ax9 = plt.subplot(3, 3, 9)
sns.barplot(data=df, x='Tier', y='Projects', ax=ax9, palette='Set2', ci=95)
ax9.set_title('Average Projects Completed by Tier', fontsize=12, weight='bold')
ax9.set_xlabel('Tier', fontsize=10)
ax9.set_ylabel('Projects Count', fontsize=10)

plt.tight_layout()
plt.savefig('student_analysis.png', dpi=300, bbox_inches='tight')
print("\n[SUCCESS] Graph saved as 'student_analysis.png'")
plt.show()

# Create detailed statistics
print("\n" + "=" * 80)
print("[STATISTICS] Detailed Analysis")
print("=" * 80)

print("\n[TIER-1 STUDENTS]")
tier1 = df[df['Tier'] == 'Tier-1']
print(f"Count: {len(tier1)}")
print(f"Average Probability: {tier1['Probability'].mean():.2%}")
print(f"Average CGPA: {tier1['CGPA'].mean():.2f}")
print(f"Average Aptitude: {tier1['Aptitude'].mean():.2f}")
print(f"Average Communication: {tier1['Communication'].mean():.2f}")
print(f"Average Technical: {tier1['Technical'].mean():.2f}")
print(f"Average Internship: {tier1['Internship'].mean():.2f}")
print(f"Average Projects: {tier1['Projects'].mean():.2f}")
print("\nStudents:")
for idx, row in tier1.iterrows():
    print(f"  - {row['Name']}: {row['Probability']:.1%} probability")

print("\n[TIER-2 STUDENTS]")
tier2 = df[df['Tier'] == 'Tier-2']
print(f"Count: {len(tier2)}")
print(f"Average Probability: {tier2['Probability'].mean():.2%}")
print(f"Average CGPA: {tier2['CGPA'].mean():.2f}")
print(f"Average Aptitude: {tier2['Aptitude'].mean():.2f}")
print(f"Average Communication: {tier2['Communication'].mean():.2f}")
print(f"Average Technical: {tier2['Technical'].mean():.2f}")
print(f"Average Internship: {tier2['Internship'].mean():.2f}")
print(f"Average Projects: {tier2['Projects'].mean():.2f}")
print("\nStudents:")
for idx, row in tier2.iterrows():
    print(f"  - {row['Name']}: {row['Probability']:.1%} probability")

print("\n[TIER-3 STUDENTS]")
tier3 = df[df['Tier'] == 'Tier-3']
print(f"Count: {len(tier3)}")
print(f"Average Probability: {tier3['Probability'].mean():.2%}")
print(f"Average CGPA: {tier3['CGPA'].mean():.2f}")
print(f"Average Aptitude: {tier3['Aptitude'].mean():.2f}")
print(f"Average Communication: {tier3['Communication'].mean():.2f}")
print(f"Average Technical: {tier3['Technical'].mean():.2f}")
print(f"Average Internship: {tier3['Internship'].mean():.2f}")
print(f"Average Projects: {tier3['Projects'].mean():.2f}")
print("\nStudents:")
for idx, row in tier3.iterrows():
    print(f"  - {row['Name']}: {row['Probability']:.1%} probability")

print("\n[BELOW TIER-3 STUDENTS]")
below = df[df['Tier'] == 'Below Tier-3']
print(f"Count: {len(below)}")
print(f"Average Probability: {below['Probability'].mean():.2%}")
print(f"Average CGPA: {below['CGPA'].mean():.2f}")
print(f"Average Aptitude: {below['Aptitude'].mean():.2f}")
print(f"Average Communication: {below['Communication'].mean():.2f}")
print(f"Average Technical: {below['Technical'].mean():.2f}")
print(f"Average Internship: {below['Internship'].mean():.2f}")
print(f"Average Projects: {below['Projects'].mean():.2f}")
print("\nStudents:")
for idx, row in below.iterrows():
    print(f"  - {row['Name']}: {row['Probability']:.1%} probability")

# Create correlation heatmap
print("\n[CREATING] Correlation Heatmap...")
fig2, ax = plt.subplots(figsize=(10, 8))
numeric_cols = ['Probability', 'CGPA', 'Aptitude', 'Communication', 'Technical', 'Internship', 'Projects']
correlation = df[numeric_cols].corr()
sns.heatmap(correlation, annot=True, fmt='.2f', cmap='coolwarm', center=0, ax=ax, 
            cbar_kws={'label': 'Correlation'}, square=True)
ax.set_title('Feature Correlation Heatmap', fontsize=14, weight='bold')
plt.tight_layout()
plt.savefig('correlation_heatmap.png', dpi=300, bbox_inches='tight')
print("[SUCCESS] Correlation heatmap saved as 'correlation_heatmap.png'")
plt.show()

print("\n" + "=" * 80)
print("[COMPLETE] Analysis finished!")
print("=" * 80)
print("\nGenerated files:")
print("  1. student_analysis.png - 9 detailed graphs")
print("  2. correlation_heatmap.png - Feature correlation")
print("\n")
