import pandas as pd
import sys

file_path = r'c:\Users\sumit\OneDrive\Desktop\New folder (13)\dataset\Students-List-15-05-2026-07-08-24-0KBlEw.xlsx'

try:
    # Read Excel file
    df = pd.read_excel(file_path, sheet_name=0)
    
    print("=" * 80)
    print("DATASET ANALYSIS")
    print("=" * 80)
    print(f"\nTotal Rows: {len(df)}")
    print(f"Total Columns: {len(df.columns)}")
    print(f"\nColumn Names:")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i}. {col}")
    
    print(f"\n\nFirst 3 Rows:")
    print(df.head(3).to_string())
    
    print(f"\n\nData Types:")
    print(df.dtypes)
    
    print(f"\n\nMissing Values:")
    missing = df.isnull().sum()
    if missing.sum() > 0:
        print(missing[missing > 0])
    else:
        print("No missing values")
    
    print(f"\n\nBasic Statistics:")
    print(df.describe())
    
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
