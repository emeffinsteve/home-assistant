#!/usr/bin/env python3
"""
Home Assistant Entity CSV Export Script - Remote Version
Creates separate CSV files for each domain and area
Run from MacBook: python3 ha_export.py
"""

import os
import csv
import json
import requests
from datetime import datetime

# Configuration - Update these with your details
HA_URL = "https://fwch7ombgixhvotfrixymjjcyokmdjvz.ui.nabu.casa"
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJlM2MyN2NmOTQ4ZDI0MTZhOGQ5OTBlNTQ0MWJjNDY5YSIsImlhdCI6MTc1MTUwNDgwMSwiZXhwIjoyMDY2ODY0ODAxfQ.Zf02zzmCIGDD9YAYFTZ-Zw8XehB5ezT8j5J5249rdkY"

# Export directory (will be created in your current folder)
EXPORT_DIR = "./ha_entity_export"

def safe_filename(name):
    """Convert area/domain name to safe filename"""
    return name.lower().replace("'", "").replace(" ", "_").replace("-", "_")

def make_api_request(endpoint):
    """Make API request to Home Assistant"""
    url = f"{HA_URL}/api/{endpoint}"
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making API request to {endpoint}: {e}")
        return None

def extract_area_from_entity(entity_id, friendly_name):
    """Extract area information from entity attributes (simplified approach)"""
    # This is a simplified approach since we can't access the registries via REST API
    # We'll try to infer area from entity naming patterns
    
    device_name = "Unknown Device"
    area_name = "Unassigned"
    
    # Common patterns in entity naming that might indicate area
    area_keywords = {
        "kitchen": "Kitchen",
        "living": "Great Room", 
        "bedroom": "Owner's Bedroom",
        "bathroom": "Main Bathroom",
        "garage": "Garage",
        "office": "Office",
        "basement": "Basement",
        "deck": "Deck",
        "foyer": "Foyer",
        "hallway": "Hallway",
        "laundry": "Laundry Room",
        "rec": "Rec Room",
        "storage": "Storage",
        "front_door": "Front Door",
        "genevieve": "Genevieve's Room",
        "ulrich": "Ulrich's Room"
    }
    
    # Check entity_id and friendly_name for area keywords
    search_text = f"{entity_id} {friendly_name}".lower()
    
    for keyword, area in area_keywords.items():
        if keyword in search_text:
            area_name = area
            break
    
    # Try to extract device name from friendly name
    if friendly_name and friendly_name != entity_id:
        # Remove common suffixes to get device name
        device_name = friendly_name
        for suffix in [" Temperature", " Humidity", " Switch", " Light", " Sensor", " Button"]:
            if device_name.endswith(suffix):
                device_name = device_name[:-len(suffix)]
                break
    
    return None, device_name, area_name

def main():
    print("🏠 Starting Home Assistant Entity Export...")
    print(f"Connecting to: {HA_URL}")
    
    # Create export directory
    try:
        os.makedirs(EXPORT_DIR, exist_ok=True)
        print(f"✅ Export directory ready: {EXPORT_DIR}")
    except Exception as e:
        print(f"❌ Failed to create export directory: {e}")
        return
    
    # Fetch data from Home Assistant APIs
    print("\n📡 Fetching data from Home Assistant...")
    
    print("  • Getting all entity states...")
    states = make_api_request("states")
    if not states:
        print("❌ Failed to get entity states")
        return
    
    print(f"✅ Found {len(states)} entities")
    print("ℹ️  Note: Using simplified device/area detection (REST API limitations)")
    
    # CSV header
    csv_header = ["Device Name", "Entity ID", "Domain", "Area"]
    
    # Get unique domains and areas from the data
    domains = set()
    areas = set()
    
    for state in states:
        domains.add(state['entity_id'].split('.')[0])
        # Extract area from entity naming (simplified)
        _, _, area = extract_area_from_entity(state['entity_id'], state['attributes'].get('friendly_name', ''))
        if area != "Unassigned":
            areas.add(area)
    
    # Add predefined areas that might not appear in entity names
    predefined_areas = [
        "Basement Bathroom", "Deck", "Foyer", "Front Door", "Garage", 
        "Genevieve's Room", "Great Room", "Hallway", "Kitchen", 
        "Laundry Room", "Main Bathroom", "Office", "Owner's Bathroom", 
        "Owner's Bedroom", "Rec Room", "Storage", "Ulrich's Room"
    ]
    areas.update(predefined_areas)
    
    domains = sorted(list(domains))
    areas = sorted(list(areas))
    
    print(f"\n📊 Found {len(domains)} domains and {len(areas)} areas")
    
    # Export by Domain
    print("\n📁 Creating domain CSV files...")
    domain_counts = {}
    
    for domain in domains:
        domain_entities = [state for state in states if state['entity_id'].split('.')[0] == domain]
        
        if not domain_entities:
            continue
        
        filename = f"{EXPORT_DIR}/{domain}.csv"
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(csv_header)
                
                for state in domain_entities:
                    device_id, device_name, area_name = extract_area_from_entity(
                        state['entity_id'], state['attributes'].get('friendly_name', '')
                    )
                    
                    friendly_name = state['attributes'].get('friendly_name', state['entity_id'])
                    
                    writer.writerow([
                        device_name,
                        state['entity_id'],
                        state['entity_id'].split('.')[0],
                        area_name
                    ])
            
            domain_counts[domain] = len(domain_entities)
            print(f"  ✅ {domain}.csv ({len(domain_entities)} entities)")
            
        except Exception as e:
            print(f"  ❌ Failed to create {domain}.csv: {e}")
    
    # Export by Area
    print("\n🏠 Creating area CSV files...")
    area_counts = {}
    
    # First, build a map of entities to areas
    entity_areas = {}
    for state in states:
        device_id, device_name, area_name = extract_area_from_entity(
            state['entity_id'], state['attributes'].get('friendly_name', '')
        )
        entity_areas[state['entity_id']] = area_name
    
    for area in areas:
        area_entities = [state for state in states if entity_areas.get(state['entity_id']) == area]
        
        if not area_entities:
            continue
        
        safe_area_name = safe_filename(area)
        filename = f"{EXPORT_DIR}/{safe_area_name}.csv"
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(csv_header)
                
                for state in area_entities:
                    device_id, device_name, area_name = extract_area_from_entity(
                        state['entity_id'], state['attributes'].get('friendly_name', '')
                    )
                    
                    friendly_name = state['attributes'].get('friendly_name', state['entity_id'])
                    
                    writer.writerow([
                        device_name,
                        state['entity_id'],
                        state['entity_id'].split('.')[0],
                        area_name
                    ])
            
            area_counts[area] = len(area_entities)
            print(f"  ✅ {safe_area_name}.csv ({len(area_entities)} entities)")
            
        except Exception as e:
            print(f"  ❌ Failed to create {safe_area_name}.csv: {e}")
    
    # Export Unassigned Entities
    print("\n❓ Creating unassigned entities file...")
    unassigned_entities = [state for state in states if entity_areas.get(state['entity_id']) == "Unassigned"]
    
    if unassigned_entities:
        filename = f"{EXPORT_DIR}/unassigned.csv"
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(csv_header)
                
                for state in unassigned_entities:
                    device_id, device_name, area_name = extract_area_from_entity(
                        state['entity_id'], state['attributes'].get('friendly_name', '')
                    )
                    
                    friendly_name = state['attributes'].get('friendly_name', state['entity_id'])
                    
                    writer.writerow([
                        device_name,
                        state['entity_id'],
                        state['entity_id'].split('.')[0],
                        area_name
                    ])
            
            print(f"  ✅ unassigned.csv ({len(unassigned_entities)} entities)")
            
        except Exception as e:
            print(f"  ❌ Failed to create unassigned.csv: {e}")
    
    # Create summary report
    print("\n📋 Creating summary report...")
    summary_filename = f"{EXPORT_DIR}/export_summary.txt"
    try:
        with open(summary_filename, 'w', encoding='utf-8') as f:
            f.write(f"Home Assistant CSV Export Summary\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Source: {HA_URL}\n")
            f.write("=" * 60 + "\n\n")
            
            f.write("DOMAIN EXPORTS:\n")
            f.write("-" * 20 + "\n")
            for domain, count in sorted(domain_counts.items()):
                f.write(f"  {domain}.csv: {count} entities\n")
            
            f.write(f"\nAREA EXPORTS:\n")
            f.write("-" * 20 + "\n")
            for area, count in sorted(area_counts.items()):
                safe_name = safe_filename(area)
                f.write(f"  {safe_name}.csv: {count} entities ({area})\n")
            
            if unassigned_entities:
                f.write(f"\nUNASSIGNED ENTITIES:\n")
                f.write("-" * 20 + "\n")
                f.write(f"  unassigned.csv: {len(unassigned_entities)} entities\n")
            
            f.write(f"\nSUMMARY:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Total entities processed: {len(states)}\n")
            f.write(f"Domain CSV files created: {len(domain_counts)}\n")
            f.write(f"Area CSV files created: {len(area_counts)}\n")
            f.write(f"Export location: {os.path.abspath(EXPORT_DIR)}\n")
        
        print(f"  ✅ Summary report created")
        
    except Exception as e:
        print(f"  ❌ Failed to create summary report: {e}")
    
    print(f"\n🎉 Export completed successfully!")
    print(f"📁 Files saved to: {os.path.abspath(EXPORT_DIR)}")
    print(f"📊 Total: {len(states)} entities exported")
    print(f"📄 {len(domain_counts)} domain files + {len(area_counts)} area files created")

if __name__ == "__main__":
    main()