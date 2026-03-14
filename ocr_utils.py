import cv2
import pytesseract
import re
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def get_gps_from_exif(image_path):
    """Extract GPS coordinates from image EXIF data"""
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        
        if not exif_data:
            return None, None
            
        gps_info = {}
        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag, tag)
            if tag_name == "GPSInfo":
                for gps_tag in value:
                    sub_tag_name = GPSTAGS.get(gps_tag, gps_tag)
                    gps_info[sub_tag_name] = value[gps_tag]
                break
                
        if not gps_info:
            return None, None
            
        def convert_to_degrees(value):
            d, m, s = value
            return d + (m / 60.0) + (s / 3600.0)
            
        lat = convert_to_degrees(gps_info.get('GPSLatitude', [0, 0, 0]))
        lon = convert_to_degrees(gps_info.get('GPSLongitude', [0, 0, 0]))
        
        if gps_info.get('GPSLatitudeRef') == 'S':
            lat = -lat
        if gps_info.get('GPSLongitudeRef') == 'W':
            lon = -lon
            
        return lat, lon
    except:
        return None, None


def extract_text_from_image(image):
    """Extract all text from image using OCR"""
    if isinstance(image, str):
        image = cv2.imread(image)
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray, config='--psm 6')
    return text.strip()


def extract_address_from_text(text):
    """Extract clean address from OCR text"""
    # Common location keywords
    location_keywords = ['nagar', 'road', 'street', 'colony', 'area', 'city', 'state', 'india', 'maharashtra', 'pune', 'mumbai', 'delhi', 'bangalore', 'hyderabad', 'chennai', 'kolkata', 'ahmedabad', 'surat', 'jaipur', 'lucknow', 'kanpur', 'nagpur', 'indore', 'thane', 'bhopal', 'visakhapatnam', 'pimpri', 'patna', 'vadodara', 'ghaziabad', 'ludhiana', 'agra', 'nashik', 'faridabad', 'meerut', 'rajkot', 'kalyan', 'vasai', 'varanasi', 'srinagar', 'aurangabad', 'dhanbad', 'amritsar', 'navi', 'allahabad', 'ranchi', 'howrah', 'coimbatore', 'jabalpur', 'gwalior', 'vijayawada', 'jodhpur', 'madurai', 'raipur', 'kota', 'guwahati', 'chandigarh', 'solapur', 'hubli', 'tiruchirappalli', 'bareilly', 'mysore', 'tiruppur', 'gurgaon', 'aligarh', 'jalandhar', 'bhubaneswar', 'salem', 'warangal', 'mira', 'bhiwandi', 'saharanpur', 'gorakhpur', 'bikaner', 'amravati', 'noida', 'jamshedpur', 'bhilai', 'cuttack', 'firozabad', 'kochi', 'nellore', 'bhavnagar', 'dehradun', 'durgapur', 'asansol', 'rourkela', 'nanded', 'kolhapur', 'ajmer', 'akola', 'gulbarga', 'jamnagar', 'ujjain', 'loni', 'siliguri', 'jhansi', 'ulhasnagar', 'jammu', 'sangli', 'mangalore', 'erode', 'belgaum', 'ambattur', 'tirunelveli', 'malegaon', 'gaya', 'jalgaon', 'udaipur', 'maheshtala']
    
    valid_lines = []
    for line in text.splitlines():
        line = re.sub(r'[^a-zA-Z0-9\s,.-]', '', line).strip()
        
        if (
            not line
            or len(line) < 4
            or "Lat" in line
            or "Long" in line
            or "GMT" in line
            or "Google" in line
            or "GPS" in line
            or "Map" in line
            or "Camera" in line
            or re.match(r'^[\d\s.,-]+$', line)
            or len([c for c in line if c.isalpha()]) < 3
        ):
            continue
            
        # Check if line contains location keywords
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in location_keywords):
            valid_lines.append(line)
    
    if not valid_lines:
        return None
        
    # Extract city, state, country pattern
    address_parts = []
    for line in valid_lines:
        # Clean up common OCR artifacts
        cleaned = re.sub(r'\b[a-zA-Z]\b', '', line)  # Remove single letters
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()  # Multiple spaces to single
        
        if len(cleaned) > 3:
            address_parts.append(cleaned)
    
    return ", ".join(address_parts[:3]) if address_parts else None  # Limit to 3 parts


def process_geotagged_image(image_path):
    """Main function to extract address and GPS coordinates from geotagged image"""
    # Extract GPS from EXIF data
    lat, lon = get_gps_from_exif(image_path)
    
    # Extract text using OCR
    image = cv2.imread(image_path)
    if image is None:
        return None, None, None
        
    text = extract_text_from_image(image)
    address = extract_address_from_text(text)
    
    # If no GPS in EXIF, try to extract from OCR text
    if lat is None or lon is None:
        lat_match = re.search(r"Lat[itude]*\s*:?\s*([\d.-]+)", text, re.IGNORECASE)
        lon_match = re.search(r"Lon[gitude]*\s*:?\s*([\d.-]+)", text, re.IGNORECASE)
        
        if lat_match:
            lat = float(lat_match.group(1))
        if lon_match:
            lon = float(lon_match.group(1))
    
    return address, lat, lon
