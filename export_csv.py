"""
CSV Export Utility for Pothole Detection Records
This script exports all detection data to CSV format
"""

import sys
from database import export_to_csv, get_all_detections

def main():
    """Main export function"""
    print("Pothole Detection Data Export Utility")
    print("=" * 40)
    
    # Check if records exist
    records = get_all_detections()
    if not records:
        print("No detection records found in database.")
        return
    
    print(f"Found {len(records)} detection records.")
    
    # Get custom filename if provided
    filename = None
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        if not filename.endswith('.csv'):
            filename += '.csv'
    
    # Export to CSV
    csv_path = export_to_csv(filename)
    
    if csv_path:
        print(f"\nExport completed successfully!")
        print(f"File location: {csv_path}")
        print(f"Records exported: {len(records)}")
    else:
        print("Export failed.")

if __name__ == "__main__":
    main()