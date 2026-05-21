#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Placement analysis by medium (English vs Hindi) with student names
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Read Excel files
dataset_path = Path("c:/Users/sumit/OneDrive/Desktop/New folder (13)/dataset")
excel_files = sorted(list(dataset_path.glob("*.xlsx")))

print("=" * 80)
print("[ANALYSIS] Placement Analysis by Medium (English vs Hindi)")
print("=" * 80)

# Read all Excel files
all_students = []
for file in excel_files:
    try:
        df = pd.read_excel(file)
        all_students.append(df)
        print(f"[OK] {file.name}: {len(df)} students")
    except Exception as e:
        print(f"[ERROR] {file.name}: {e}")

if all_students:
    # Combine all data
    combined_df = pd.concat(all_students, ignore_index=True)
    print(f"\n[TOTAL] {len(combined_df)} students combined")
    
    # Create full name
    combined_df['Full Name'] = combined_df['First Name'].fillna('') + ' ' + combined_df['Last Name'].fillna('')
    combined_df['Full Name'] = combined_df['Full Name'].str.strip()
    
    # Get relevant columns
    analysis_df = combined_df[['Full Name', '12th - Medium', 'Job Offer Count', 'Current Academics Aggregate Marks']].copy()
    analysis_df.columns = ['Name', 'Medium', 'Job Offers', 'CGPA']
    
    # Clean data
    analysis_df['Medium'] = analysis_df['Medium'].fillna('Unknown')
    analysis_df['Job Offers'] = pd.to_numeric(analysis_df['Job Offers'], errors='coerce').fillna(0).astype(int)
    analysis_df['CGPA'] = pd.to_numeric(analysis_df['CGPA'], errors='coerce').fillna(0)
    
    # Create placement status
    analysis_df['Placed'] = analysis_df['Job Offers'] > 0
    
    print(f"\n[MEDIUM DISTRIBUTION]")
    print(analysis_df['Medium'].value_counts())
    
    print(f"\n[PLACEMENT STATISTICS]")
    print(f"Total Students: {len(analysis_df)}")
    print(f"Placed Students: {analysis_df['Placed'].sum()}")
    print(f"Placement Rate: {(analysis_df['Placed'].sum() / len(analysis_df) * 100):.2f}%")
    
    # Analysis by medium
    print(f"\n[ENGLISH MEDIUM]")
    english = analysis_df[analysis_df['Medium'].str.contains('English', case=False, na=False)]
    print(f"Total: {len(english)}")
    print(f"Placed: {english['Placed'].sum()}")
    print(f"Placement Rate: {(english['Placed'].sum() / len(english) * 100):.2f}%")
    print(f"Avg CGPA: {english['CGPA'].mean():.2f}")
    print(f"Avg Job Offers: {english['Job Offers'].mean():.2f}")
    
    print(f"\n[HINDI MEDIUM]")
    hindi = analysis_df[analysis_df['Medium'].str.contains('Hindi', case=False, na=False)]
    print(f"Total: {len(hindi)}")
    print(f"Placed: {hindi['Placed'].sum()}")
    print(f"Placement Rate: {(hindi['Placed'].sum() / len(hindi) * 100):.2f}%")
    print(f"Avg CGPA: {hindi['CGPA'].mean():.2f}")
    print(f"Avg Job Offers: {hindi['Job Offers'].mean():.2f}")
    
    # Top placed students
    print(f"\n[TOP PLACED STUDENTS - ENGLISH MEDIUM]")
    top_english = english[english['Placed']].nlargest(10, 'Job Offers')[['Name', 'Job Offers', 'CGPA']]
    for idx, row in top_english.iterrows():
        print(f"  {row['Name']}: {int(row['Job Offers'])} offers, CGPA: {row['CGPA']:.2f}")
    
    print(f"\n[TOP PLACED STUDENTS - HINDI MEDIUM]")
    top_hindi = hindi[hindi['Placed']].nlargest(10, 'Job Offers')[['Name', 'Job Offers', 'CGPA']]
    for idx, row in top_hindi.iterrows():
        print(f"  {row['Name']}: {int(row['Job Offers'])} offers, CGPA: {row['CGPA']:.2f}")
    
    # Create visualizations
    print(f"\n[CREATING] Visualizations...")
    
    fig = plt.figure(figsize=(20, 12))
    
    # 1. Placement Rate Comparison
    ax1 = plt.subplot(2, 3, 1)
    placement_by_medium = analysis_df.groupby('Medium')['Placed'].agg(['sum', 'count'])
    placement_by_medium['rate'] = (placement_by_medium['sum'] / placement_by_medium['count'] * 100)
    placement_by_medium['rate'].plot(kind='bar', ax=ax1, color=['#3b82f6', '#ef4444', '#10b981'])
    ax1.set_title('Placement Rate by Medium (%)', fontsize=12, weight='bold')
    ax1.set_ylabel('Placement Rate (%)')
    ax1.set_xlabel('Medium')
    ax1.tick_params(axis='x', rotation=45)
    for i, v in enumerate(placement_by_medium['rate']):
        ax1.text(i, v + 1, f'{v:.1f}%', ha='center', weight='bold')
    
    # 2. Student Count by Medium
    ax2 = plt.subplot(2, 3, 2)
    medium_counts = analysis_df['Medium'].value_counts()
    colors = ['#3b82f6', '#ef4444', '#10b981'][:len(medium_counts)]
    ax2.pie(medium_counts.values, labels=medium_counts.index, autopct='%1.1f%%', colors=colors)
    ax2.set_title('Student Distribution by Medium', fontsize=12, weight='bold')
    
    # 3. Average CGPA by Medium
    ax3 = plt.subplot(2, 3, 3)
    cgpa_by_medium = analysis_df.groupby('Medium')['CGPA'].mean()
    cgpa_by_medium.plot(kind='bar', ax=ax3, color=['#3b82f6', '#ef4444', '#10b981'][:len(cgpa_by_medium)])
    ax3.set_title('Average CGPA by Medium', fontsize=12, weight='bold')
    ax3.set_ylabel('Average CGPA')
    ax3.set_xlabel('Medium')
    ax3.tick_params(axis='x', rotation=45)
    for i, v in enumerate(cgpa_by_medium):
        ax3.text(i, v + 0.05, f'{v:.2f}', ha='center', weight='bold')
    
    # 4. Job Offers Distribution
    ax4 = plt.subplot(2, 3, 4)
    sns.boxplot(data=analysis_df, x='Medium', y='Job Offers', ax=ax4)
    ax4.set_title('Job Offers Distribution by Medium', fontsize=12, weight='bold')
    ax4.set_ylabel('Number of Job Offers')
    ax4.set_xlabel('Medium')
    
    # 5. Placed vs Not Placed
    ax5 = plt.subplot(2, 3, 5)
    placement_counts = analysis_df.groupby(['Medium', 'Placed']).size().unstack(fill_value=0)
    placement_counts.plot(kind='bar', ax=ax5, color=['#ef4444', '#10b981'])
    ax5.set_title('Placed vs Not Placed by Medium', fontsize=12, weight='bold')
    ax5.set_ylabel('Count')
    ax5.set_xlabel('Medium')
    ax5.legend(['Not Placed', 'Placed'])
    ax5.tick_params(axis='x', rotation=45)
    
    # 6. CGPA vs Job Offers
    ax6 = plt.subplot(2, 3, 6)
    for medium in analysis_df['Medium'].unique():
        data = analysis_df[analysis_df['Medium'] == medium]
        ax6.scatter(data['CGPA'], data['Job Offers'], label=medium, alpha=0.6, s=50)
    ax6.set_title('CGPA vs Job Offers by Medium', fontsize=12, weight='bold')
    ax6.set_xlabel('CGPA')
    ax6.set_ylabel('Job Offers')
    ax6.legend()
    ax6.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('medium_placement_analysis.png', dpi=300, bbox_inches='tight')
    print("[SUCCESS] Saved: medium_placement_analysis.png")
    
    # Create detailed report
    print(f"\n[CREATING] Detailed Report...")
    
    report = f"""
PLACEMENT ANALYSIS BY MEDIUM (ENGLISH vs HINDI)
{'=' * 80}

OVERALL STATISTICS:
- Total Students: {len(analysis_df)}
- Placed Students: {analysis_df['Placed'].sum()}
- Overall Placement Rate: {(analysis_df['Placed'].sum() / len(analysis_df) * 100):.2f}%

ENGLISH MEDIUM:
- Total Students: {len(english)}
- Placed Students: {english['Placed'].sum()}
- Placement Rate: {(english['Placed'].sum() / len(english) * 100):.2f}%
- Average CGPA: {english['CGPA'].mean():.2f}
- Average Job Offers: {english['Job Offers'].mean():.2f}
- Max Job Offers: {english['Job Offers'].max():.0f}

HINDI MEDIUM:
- Total Students: {len(hindi)}
- Placed Students: {hindi['Placed'].sum()}
- Placement Rate: {(hindi['Placed'].sum() / len(hindi) * 100):.2f}%
- Average CGPA: {hindi['CGPA'].mean():.2f}
- Average Job Offers: {hindi['Job Offers'].mean():.2f}
- Max Job Offers: {hindi['Job Offers'].max():.0f}

TOP 10 PLACED STUDENTS - ENGLISH MEDIUM:
"""
    for idx, (i, row) in enumerate(top_english.iterrows(), 1):
        report += f"{idx}. {row['Name']}: {int(row['Job Offers'])} offers, CGPA: {row['CGPA']:.2f}\n"
    
    report += f"\nTOP 10 PLACED STUDENTS - HINDI MEDIUM:\n"
    for idx, (i, row) in enumerate(top_hindi.iterrows(), 1):
        report += f"{idx}. {row['Name']}: {int(row['Job Offers'])} offers, CGPA: {row['CGPA']:.2f}\n"
    
    with open('medium_placement_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    print("[SUCCESS] Saved: medium_placement_report.txt")
    
    print(f"\n[COMPLETE] Analysis finished!")
    print(f"\nGenerated files:")
    print(f"  1. medium_placement_analysis.png - 6 detailed graphs")
    print(f"  2. medium_placement_report.txt - Detailed report")

else:
    print("\n[ERROR] No data found")

print("\n" + "=" * 80)
