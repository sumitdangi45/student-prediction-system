import pandas as pd
import os

dataset_dir = r'c:\Users\sumit\OneDrive\Desktop\New folder (13)\dataset'

files = [
    'Students-List-15-05-2026-07-08-24-0KBlEw.xlsx',
    'Students-List-15-05-2026-08-14-30-puVIEw.xlsx',
    'Students-List-15-05-2026-08-54-10-zBSlEw.xlsx',
    'Students-List-15-05-2026-09-00-36-RoOXEw.xlsx'
]

print("=" * 80)
print("DATASET FILES ANALYSIS")
print("=" * 80)

total_students = 0

for file in files:
    file_path = os.path.join(dataset_dir, file)
    try:
        df = pd.read_excel(file_path)
        num_students = len(df)
        total_students += num_students
        print(f"\n📄 {file}")
        print(f"   Students: {num_students}")
        print(f"   Columns: {len(df.columns)}")
    except Exception as e:
        print(f"\n❌ {file}: Error - {e}")

print("\n" + "=" * 80)
print(f"✅ TOTAL STUDENTS: {total_students}")
print("=" * 80)
