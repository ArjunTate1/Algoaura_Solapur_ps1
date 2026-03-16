"""
INTERNAL USE ONLY - Admin script for pothole detection records
This script provides authorized access to view and export detection data
"""

import os
from database import get_all_detections, export_to_csv

def view_detection_records():
    """View all stored detection records - INTERNAL USE ONLY"""
    print("=== POTHOLE DETECTION RECORDS (INTERNAL ACCESS) ===\n")
    
    records = get_all_detections()
    
    if not records:
        print("No detection records found.")
        return
    
    for i, record in enumerate(records, 1):
        print(f"Record {i}:")
        print(f"  ID: {record[0]}")
        print(f"  Image Path: {record[1]}")
        print(f"  Longitude: {record[2]}")
        print(f"  Latitude: {record[3]}")
        print(f"  Address: {record[4]}")
        print(f"  Potholes: {record[5]}")
        print(f"  Confidence: {record[6]}")
        print(f"  Timestamp: {record[7]}")
        print("-" * 50)
    
    print(f"\nTotal records: {len(records)}")

def admin_menu():
    """Admin menu for database operations"""
    while True:
        print("\n=== ADMIN MENU ===")
        print("1. View all records")
        print("2. Export all to CSV (overwrite)")
        print("3. Exit")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == '1':
            view_detection_records()
        elif choice == '2':
            csv_path = export_to_csv()
            if csv_path:
                print(f"\nCSV exported successfully to: {csv_path}")
        elif choice == '3':
            print("Exiting admin panel.")
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    # Simple authentication check
    auth_key = input("Enter admin access key: ")
    if auth_key == "PotholeAdmin2024!":  # Secure admin key
        admin_menu()
    else:
        print("Access denied.")