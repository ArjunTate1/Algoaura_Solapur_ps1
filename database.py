import sqlite3
import uuid
import os
import csv
from datetime import datetime

# Private storage directories
PRIVATE_DIR = 'private_data'
DB_DIR = os.path.join(PRIVATE_DIR, 'database')
IMAGE_DIR = os.path.join(PRIVATE_DIR, 'images')
EXPORT_DIR = 'exports'

def ensure_directories():
    """Create all required directories"""
    os.makedirs(DB_DIR, exist_ok=True)
    os.makedirs(IMAGE_DIR, exist_ok=True)
    os.makedirs(EXPORT_DIR, exist_ok=True)

def init_database():
    """Initialize the SQLite database and create table"""
    ensure_directories()
    db_path = os.path.join(DB_DIR, 'pothole_data.db')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pothole_detections (
            id TEXT PRIMARY KEY,
            image_path TEXT,
            longitude REAL,
            latitude REAL,
            address TEXT,
            num_potholes INTEGER,
            confidence_level REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def save_image_and_detection(image_array, longitude, latitude, address, num_potholes, confidence_level):
    """Save image to private storage and detection data to database"""
    ensure_directories()
    
    # Generate unique filename
    unique_id = str(uuid.uuid4())
    image_filename = f"{unique_id}.jpg"
    image_path = os.path.join(IMAGE_DIR, image_filename)
    
    # Save image to private storage
    import cv2
    cv2.imwrite(image_path, image_array)
    
    # Get current timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Save detection data to database
    db_path = os.path.join(DB_DIR, 'pothole_data.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO pothole_detections 
        (id, image_path, longitude, latitude, address, num_potholes, confidence_level)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (unique_id, image_path, longitude, latitude, address, num_potholes, confidence_level))
    
    conn.commit()
    conn.close()
    
    # Append to CSV file immediately
    append_to_csv(unique_id, image_path, longitude, latitude, 
                  address, num_potholes, confidence_level, timestamp)
    
    return unique_id

def get_all_detections():
    """Get all detection records - INTERNAL USE ONLY"""
    db_path = os.path.join(DB_DIR, 'pothole_data.db')
    if not os.path.exists(db_path):
        return []
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM pothole_detections ORDER BY timestamp DESC')
    records = cursor.fetchall()
    
    conn.close()
    return records

def append_to_csv(detection_id, image_path, longitude, latitude, address, num_potholes, confidence_level, timestamp):
    """Append single detection record to fixed CSV file"""
    ensure_directories()
    
    csv_path = os.path.join(EXPORT_DIR, 'pothole_records.csv')
    headers = ['ID', 'Image_Path', 'Longitude', 'Latitude', 'Address', 
               'Num_Potholes', 'Confidence_Level', 'Timestamp']
    
    # Check if file exists and write headers if needed
    file_exists = os.path.exists(csv_path)
    
    with open(csv_path, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write headers only if file doesn't exist
        if not file_exists:
            writer.writerow(headers)
        
        # Append the new record
        writer.writerow([detection_id, image_path, longitude, latitude, 
                        address, num_potholes, confidence_level, timestamp])
    
    return csv_path

def export_to_csv(filename=None):
    """Export all detection records to CSV file"""
    ensure_directories()
    
    if filename is None:
        filename = 'pothole_records.csv'  # Fixed filename
    
    csv_path = os.path.join(EXPORT_DIR, filename)
    records = get_all_detections()
    
    if not records:
        print("No records to export.")
        return None
    
    headers = ['ID', 'Image_Path', 'Longitude', 'Latitude', 'Address', 
               'Num_Potholes', 'Confidence_Level', 'Timestamp']
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerows(records)
    
    print(f"Exported {len(records)} records to {csv_path}")
    return csv_path