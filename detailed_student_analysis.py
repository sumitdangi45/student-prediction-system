#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Detailed student analysis with names and medium comparison
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import openpyxl
from pathlib import Path
import os

# Read Excel files
dataset_path = Path("c:/Users/sumit/OneDrive/Desktop/New folder (13)/dataset")
excel_files = list(dataset_path.glob("*.xlsx"))

print("=" * 80)
print("[ANALYSIS] Detailed Student Analysis with Names")
print("=" * 80)
print(f"\n[INFO] Found {len(excel_files)} Excel files")

# Read all Excel files
all_students = []
for file in excel_files:
    print(f"\n[READING] {file.name}")
    try:
        df = pd.read_excel(file)
        print(f"   Columns: {list(df.columns)}")
        print(f"   Rows: {len(df)}")
        all_students.append(df)
    except Exception as e:
        print(f"   Error: {e}")

if all_students:
    # Combine all data
    combined_df = pd.concat(all_students, ignore_index=True)
    print(f"\n[COMBINED] Total students: {len(combined_df)}")
    print(f"\n[COLUMNS] Available columns:")
    for i, col in enumerate(combined_df.columns, 1):
        print(f"   {i}. {col}")
    
    print(f"\n[SAMPLE DATA]")
    print(combined_df.head(10))
    
    # Check for medium column
    medium_cols = [col for col in combined_df.columns if 'medium' in col.lower() or 'language' in col.lower()]
    print(f"\n[MEDIUM COLUMNS] {medium_cols}")
    
    # Check for placement column
    placement_cols = [col for col in combined_df.columns if 'placed' in col.lower() or 'placement' in col.lower()]
    print(f"\n[PLACEMENT COLUMNS] {placement_cols}")
    
    # Show all data
    print(f"\n[ALL DATA]")
    print(combined_df.to_string())
    
else:
    print("\n[ERROR] No Excel files found or could not read them")

print("\n" + "=" * 80)
