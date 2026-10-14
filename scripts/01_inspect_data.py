
from pathlib import Path
import pandas as pd

# Locate the project and raw dataset
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"

# Find supported dataset files
files = [
    *RAW_DIR.glob("*.xlsx"),
    *RAW_DIR.glob("*.xls"),
    *RAW_DIR.glob("*.csv"),
]

if not files:
    raise FileNotFoundError(
        f"No Excel or CSV dataset found in {RAW_DIR}"
    )

# Use the first matching file
file_path = files[0]
print(f"Loading: {file_path.name}")

# Load the dataset
if file_path.suffix.lower() == ".csv":
    df = pd.read_csv(file_path)
else:
    df = pd.read_excel(file_path)

# Inspect the data
print("\n--- Dataset Shape ---")
print(f"Rows: {df.shape[0]:,}")
print(f"Columns: {df.shape[1]}")

print("\n--- Column Names ---")
print(df.columns.tolist())

print("\n--- First 5 Rows ---")
print(df.head())

print("\n--- Data Types ---")
print(df.dtypes)

print("\n--- Missing Values ---")
print(df.isnull().sum())

print("\n--- Duplicate Rows ---")
print(f"Exact duplicates: {df.duplicated().sum():,}")

print("\n--- Numeric Summary ---")
print(df.select_dtypes(include="number").describe())

print("\nDataset inspection completed successfully.")
