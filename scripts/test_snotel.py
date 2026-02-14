"""
Test SNOTEL data fetching with a known working station
"""

from metloom.pointdata import SnotelPointData
from metloom.variables import SnotelVariables
from datetime import datetime, timedelta
import pandas as pd

# Use FULL TRIPLET format: station_id:state:network
station_triplet = "663:CO:SNTL"
station_name = "Niwot"

print(f"Testing SNOTEL station: {station_triplet} ({station_name})")
print("="*60)

try:
    # Initialize point data with triplet
    point = SnotelPointData(station_triplet, "SNOTEL")
    print(f"✓ Station initialized: {point.name}")
    
    # Query PAST data (SNOTEL has historical data, not real-time)
    # Go back 10-20 days to be safe
    end_date = datetime.now() - timedelta(days=10)  # 10 days ago
    start_date = end_date - timedelta(days=7)       # 17 days ago
    
    print(f"\nQuerying HISTORICAL data from {start_date.date()} to {end_date.date()}...")
    
    # Get data
    df = point.get_daily_data(
        start_date=start_date,
        end_date=end_date,
        variables=[
            SnotelVariables.SNOWDEPTH,
            SnotelVariables.SWE,
            SnotelVariables.TEMP
        ]
    )
    
    print(f"\n✓ Data retrieved!")
    print(f"Shape: {df.shape}")
    print(f"\nColumns: {list(df.columns)}")
    print(f"\nData:\n{df}")
    
    # Show column names and types
    print(f"\nColumn details:")
    for col in df.columns:
        print(f"  {col}: {type(col)}")
        if len(df) > 0:
            print(f"    Sample value: {df[col].iloc[0]}")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()