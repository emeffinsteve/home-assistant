"""
Home Assistant Entity CSV Export Script
Creates separate CSV files for each domain and area
Run with: python_script.export_entities
"""

import os
import csv
from datetime import datetime

def safe_filename(name):
    """Convert area/domain name to safe filename"""
    return name.lower().replace("'", "").replace(" ", "_").replace("-", "_")

def get_device_info(entity_id):
    """Get device ID and name for an entity"""
    try:
        # Get registries
        entity_reg = hass.helpers.entity_registry.async_get(hass)
        device_reg = hass.helpers.device_registry.async_get(hass)
        
        # Get entity entry
        entity_entry = entity_reg.async_get(entity_id)
        if entity_entry and entity_entry.device_id:
            device_entry = device_reg.async_get(entity_entry.device_id)
            if device_entry:
                device_name = device_entry.name_by_user or device_entry.name or "Unknown Device"
                return entity_entry.device_id, device_name
        
        return None, "No Device"
    except Exception as e:
        logger.warning(f"Error getting device info for {entity_id}: {e}")
        return None, "No Device"

def get_area_name(entity_id):
    """Get area name for an entity"""
    try:
        entity_reg = hass.helpers.entity_registry.async_get(hass)
        area_reg = hass.helpers.area_registry.async_get(hass)
        
        # Get entity entry
        entity_entry = entity_reg.async_get(entity_id)
        
        # Check entity area first
        if entity_entry and entity_entry.area_id:
            area_entry = area_reg.async_get_area(entity_entry.area_id)
            if area_entry:
                return area_entry.name
        
        # Check device area
        if entity_entry and entity_entry.device_id:
            device_reg = hass.helpers.device_registry.async_get(hass)
            device_entry = device_reg.async_get(entity_entry.device_id)
            if device_entry and device_entry.area_id:
                area_entry = area_reg.async_get_area(device_entry.area_id)
                if area_entry:
                    return area_entry.name
        
        return "Unassigned"
    except Exception as e:
        logger.warning(f"Error getting area for {entity_id}: {e}")
        return "Unassigned"

# Create export directory
export_dir = "/config/exportcsv"
try:
    os.makedirs(export_dir, exist_ok=True)
    logger.info(f"Export directory created/verified: {export_dir}")
except Exception as e:
    logger.error(f"Failed to create export directory: {e}")
    exit()

# Get all states
states = hass.states.all()
logger.info(f"Found {len(states)} total entities")

# CSV header
csv_header = ["Friendly Name", "Device Name", "Device ID", "Entity ID", "Domain", "Area", "State", "Last Updated"]

# Define your areas and domains
areas = [
    "Basement Bathroom", "Deck", "Foyer", "Front Door", "Garage", 
    "Genevieve's Room", "Great Room", "Hallway", "Kitchen", 
    "Laundry Room", "Main Bathroom", "Office", "Owner's Bathroom", 
    "Owner's Bedroom", "Rec Room", "Storage", "Ulrich's Room"
]

domains = [
    "automation", "binary_sensor", "button", "calendar", "camera", 
    "climate", "conversation", "cover", "device_tracker", "event", 
    "fan", "govee", "image", "input_boolean", "input_button", 
    "input_datetime", "input_number", "input_select", "input_text", 
    "light", "lock", "media_player", "number", "person", "remote", 
    "script", "select", "sensor", "siren", "stt", "sun", "switch", 
    "time", "timer", "todo", "tts", "update", "vacuum", "weather", "zone"
]

# Export by Domain
logger.info("Starting domain CSV exports...")
domain_counts = {}

for domain in domains:
    domain_entities = [state for state in states if state.domain == domain]
    
    if not domain_entities:
        logger.info(f"No entities found for domain: {domain}")
        continue
    
    filename = f"{export_dir}/{domain}.csv"
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(csv_header)
            
            for state in domain_entities:
                device_id, device_name = get_device_info(state.entity_id)
                area_name = get_area_name(state.entity_id)
                friendly_name = state.attributes.get('friendly_name', state.entity_id)
                last_updated = state.last_updated.strftime('%Y-%m-%d %H:%M:%S') if state.last_updated else 'Unknown'
                
                writer.writerow([
                    friendly_name,
                    device_name,
                    device_id or 'None',
                    state.entity_id,
                    state.domain,
                    area_name,
                    str(state.state),
                    last_updated
                ])
        
        domain_counts[domain] = len(domain_entities)
        logger.info(f"✓ Exported {len(domain_entities)} {domain} entities")
        
    except Exception as e:
        logger.error(f"Failed to export {domain}.csv: {e}")

# Export by Area
logger.info("Starting area CSV exports...")
area_counts = {}

for area in areas:
    area_entities = [state for state in states if get_area_name(state.entity_id) == area]
    
    if not area_entities:
        logger.info(f"No entities found for area: {area}")
        continue
    
    safe_area_name = safe_filename(area)
    filename = f"{export_dir}/{safe_area_name}.csv"
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(csv_header)
            
            for state in area_entities:
                device_id, device_name = get_device_info(state.entity_id)
                area_name = get_area_name(state.entity_id)
                friendly_name = state.attributes.get('friendly_name', state.entity_id)
                last_updated = state.last_updated.strftime('%Y-%m-%d %H:%M:%S') if state.last_updated else 'Unknown'
                
                writer.writerow([
                    friendly_name,
                    device_name,
                    device_id or 'None',
                    state.entity_id,
                    state.domain,
                    area_name,
                    str(state.state),
                    last_updated
                ])
        
        area_counts[area] = len(area_entities)
        logger.info(f"✓ Exported {len(area_entities)} entities from {area}")
        
    except Exception as e:
        logger.error(f"Failed to export {safe_area_name}.csv: {e}")

# Export Unassigned Entities
unassigned_entities = [state for state in states if get_area_name(state.entity_id) == "Unassigned"]
if unassigned_entities:
    filename = f"{export_dir}/unassigned.csv"
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(csv_header)
            
            for state in unassigned_entities:
                device_id, device_name = get_device_info(state.entity_id)
                area_name = get_area_name(state.entity_id)
                friendly_name = state.attributes.get('friendly_name', state.entity_id)
                last_updated = state.last_updated.strftime('%Y-%m-%d %H:%M:%S') if state.last_updated else 'Unknown'
                
                writer.writerow([
                    friendly_name,
                    device_name,
                    device_id or 'None',
                    state.entity_id,
                    state.domain,
                    area_name,
                    str(state.state),
                    last_updated
                ])
        
        logger.info(f"✓ Exported {len(unassigned_entities)} unassigned entities")
        
    except Exception as e:
        logger.error(f"Failed to export unassigned.csv: {e}")

# Create summary report
summary_filename = f"{export_dir}/export_summary.txt"
try:
    with open(summary_filename, 'w', encoding='utf-8') as f:
        f.write(f"CSV Export Summary - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 50 + "\n\n")
        
        f.write("DOMAIN EXPORTS:\n")
        for domain, count in domain_counts.items():
            f.write(f"  {domain}.csv: {count} entities\n")
        
        f.write(f"\nAREA EXPORTS:\n")
        for area, count in area_counts.items():
            safe_name = safe_filename(area)
            f.write(f"  {safe_name}.csv: {count} entities ({area})\n")
        
        if unassigned_entities:
            f.write(f"\nUNASSIGNED:\n")
            f.write(f"  unassigned.csv: {len(unassigned_entities)} entities\n")
        
        f.write(f"\nTOTAL ENTITIES PROCESSED: {len(states)}\n")
        f.write(f"EXPORT LOCATION: {export_dir}\n")
    
    logger.info(f"✓ Summary report created: {summary_filename}")
    
except Exception as e:
    logger.error(f"Failed to create summary report: {e}")

logger.info("CSV export completed successfully!")
logger.info(f"Files created in: {export_dir}")
logger.info(f"Total entities processed: {len(states)}")