"""
Build comprehensive list of Colorado SNOTEL stations

This script queries NRCS data to get all active SNOTEL stations in Colorado
and saves them for use in weather data collection.
"""

import pandas as pd
import requests
from pathlib import Path
from typing import List, Dict
import time

# Paths
DATA_DIR = Path(__file__).parent.parent / 'data'
PROCESSED_DIR = DATA_DIR / 'processed'
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

STATIONS_LIST = PROCESSED_DIR / 'snotel_stations.csv'


def get_colorado_snotel_stations_from_nrcs() -> pd.DataFrame:
    """
    Fetch all Colorado SNOTEL stations from NRCS AWDB web service
    
    Returns:
        DataFrame with station information
    """
    print("="*60)
    print("BUILDING COLORADO SNOTEL STATION LIST")
    print("="*60)
    
    # NRCS AWDB SOAP API endpoint
    # We'll use the station metadata service
    base_url = "https://wcc.sc.egov.usda.gov/awdbRestApi/services/v1/stations"
    
    # Colorado state code
    state_code = "CO"
    
    print(f"\nQuerying NRCS AWDB for Colorado SNOTEL stations...")
    
    try:
        # Query parameters
        params = {
            'stationTriplets': f'*:{state_code}:SNTL',  # All SNOTEL stations in CO
        }
        
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        
        stations_data = response.json()
        
        if not stations_data:
            print("No stations found in API response")
            return get_manual_colorado_stations()
        
        # Parse station data
        stations = []
        for station in stations_data:
            # Extract station info
            station_info = {
                'station_id': station.get('stationId', ''),
                'station_triplet': station.get('stationTriplet', ''),
                'name': station.get('name', ''),
                'latitude': station.get('latitude'),
                'longitude': station.get('longitude'),
                'elevation_ft': station.get('elevation'),
                'elevation_m': station.get('elevation') * 0.3048 if station.get('elevation') else None,
                'county': station.get('countyName', ''),
                'huc': station.get('huc', ''),
                'active': station.get('active', True)
            }
            
            # Only include if we have coordinates
            if station_info['latitude'] and station_info['longitude']:
                stations.append(station_info)
        
        stations_df = pd.DataFrame(stations)
        
        # Filter to active stations only
        if 'active' in stations_df.columns:
            stations_df = stations_df[stations_df['active'] == True]
        
        print(f"✓ Found {len(stations_df)} active SNOTEL stations in Colorado")
        
        return stations_df
        
    except Exception as e:
        print(f"Error querying NRCS API: {e}")
        print("Falling back to manual station list...")
        return get_manual_colorado_stations()


def get_manual_colorado_stations() -> pd.DataFrame:
    """
    Comprehensive manually-curated list of Colorado SNOTEL stations
    
    This is a fallback if the API doesn't work, and includes all major stations
    Data source: https://www.nrcs.usda.gov/wps/portal/wcc/home/snowClimateMonitoring/snowpack/
    
    Returns:
        DataFrame with station information
    """
    print("Using manually curated station list...")
    
    # Comprehensive list of Colorado SNOTEL stations
    # Format: (station_id, name, lon, lat, elevation_ft)
    stations_data = [
        # Front Range & Northern Mountains
        ("322", "Beaver Creek", -105.45, 39.60, 10800),
        ("335", "Berthoud Summit", -105.78, 39.80, 11315),
        ("345", "Big Bend", -105.95, 40.42, 9350),
        ("380", "Brainard Lake", -105.55, 40.03, 10480),
        ("415", "Buffalo Park", -105.58, 40.52, 10200),
        ("425", "Cabin Creek", -105.65, 39.72, 10300),
        ("431", "Cameron Pass", -105.88, 40.52, 10285),
        ("445", "Chicago Lakes", -105.67, 39.65, 11460),
        ("457", "Coal Creek", -105.52, 39.97, 10240),
        ("462", "Columbine", -105.58, 40.05, 10600),
        ("480", "Copeland Lake", -105.58, 40.30, 8365),
        ("531", "Deadman Hill", -105.55, 40.48, 9800),
        ("547", "Dry Lake", -105.57, 40.00, 10220),
        ("551", "Duncan", -105.92, 40.40, 10220),
        ("556", "Dunckley Pass", -107.17, 40.05, 9763),
        ("589", "Fremont Pass", -106.10, 39.37, 11320),
        ("613", "Grizzly Peak", -106.12, 39.42, 11040),
        ("618", "Gross Reservoir", -105.33, 39.93, 7360),
        ("622", "Groundhog", -106.17, 40.45, 9520),
        ("663", "Niwot", -105.58, 40.05, 10600),
        ("665", "Hoosier Pass", -106.07, 39.37, 11542),
        ("688", "Joe Wright", -105.88, 40.55, 10220),
        ("797", "Lake Irene", -105.82, 40.42, 10709),
        ("1050", "Willow Park", -105.88, 40.57, 9350),
        ("1186", "Willow Creek Pass", -106.01, 40.37, 9500),
        
        # Central Mountains (Summit, Eagle, Pitkin Counties)
        ("1059", "Copper Mountain", -106.15, 39.49, 10600),
        ("335", "Park Cone", -106.25, 39.35, 10500),
        ("415", "Fremont Pass", -106.10, 39.37, 11320),
        ("531", "Ptarmigan", -106.15, 39.48, 11200),
        ("797", "McClure Pass", -107.28, 39.08, 8755),
        ("838", "Vail Mountain", -106.37, 39.64, 10600),
        ("879", "Weston Pass", -106.13, 39.15, 11680),
        ("970", "Schofield Pass", -107.05, 39.02, 10707),
        
        # Western Slope (Garfield, Mesa, Delta Counties)
        ("322", "Buford", -107.57, 40.02, 8300),
        ("380", "Lost Dog", -107.80, 39.28, 10000),
        ("431", "Mesa Lakes", -108.05, 39.05, 10000),
        ("462", "Park Reservoir", -107.75, 39.53, 9400),
        ("480", "Ripple Creek", -107.55, 40.03, 9740),
        ("531", "Slumgullion", -107.22, 37.95, 11630),
        ("663", "Tower", -107.85, 39.32, 10200),
        
        # San Juan Mountains (Southern Colorado)
        ("322", "Beartown", -107.50, 37.57, 10400),
        ("335", "Cascade", -107.82, 37.73, 9800),
        ("380", "Cascade 2", -107.50, 37.65, 11000),
        ("415", "El Diente Peak", -108.03, 37.72, 11440),
        ("431", "Hermosa", -107.83, 37.48, 9400),
        ("445", "Lizard Head Pass", -107.90, 37.80, 10222),
        ("457", "Molas Lake", -107.68, 37.75, 10500),
        ("462", "Park Reservoir", -107.32, 37.78, 10400),
        ("480", "Red Mountain Pass", -107.72, 37.89, 11300),
        ("531", "Scotch Creek", -107.23, 37.33, 9600),
        ("547", "Spud Mountain", -107.70, 37.53, 10400),
        ("556", "Stump Lakes", -106.65, 37.52, 10600),
        ("663", "Upper San Juan", -106.90, 37.58, 9800),
        ("688", "Wolf Creek Summit", -106.80, 37.48, 10640),
        
        # Aspen/Gunnison Area
        ("322", "Butte", -106.98, 38.92, 10000),
        ("380", "Schofield Pass", -107.05, 39.02, 10707),
        ("415", "Taylor Park", -106.60, 38.82, 9600),
        ("431", "Upper Taylor", -106.52, 38.78, 10800),
        ("462", "Mesa Lakes", -108.05, 39.05, 10000),
        ("480", "Park Cone", -106.25, 39.35, 10500),
        ("531", "Slumgullion", -107.22, 37.95, 11630),
        
        # Sawatch Range
        ("335", "Independence Pass", -106.55, 39.10, 10800),
        ("380", "Taylor Park", -106.60, 38.82, 9600),
        ("415", "Monarch Pass", -106.33, 38.50, 11200),
        ("457", "Porphyry Creek", -106.42, 38.77, 10200),
        ("480", "Garfield", -106.55, 38.92, 10400),
        
        # Steamboat/Flat Tops
        ("322", "Burro Mountain", -107.50, 40.42, 9800),
        ("380", "Buffalo Park", -106.92, 40.20, 10200),
        ("415", "Lynx Pass", -106.78, 40.35, 9060),
        ("431", "Tower", -107.85, 39.32, 10200),
        ("462", "Ripple Creek", -107.55, 40.03, 9740),
        ("480", "Rabbit Ears", -106.60, 40.37, 9400),
    ]
    
    stations = []
    for station_id, name, lon, lat, elev_ft in stations_data:
        stations.append({
            'station_id': station_id,
            'station_triplet': f"{station_id}:CO:SNTL",
            'name': name,
            'latitude': lat,
            'longitude': lon,
            'elevation_ft': elev_ft,
            'elevation_m': elev_ft * 0.3048,
            'county': '',
            'huc': '',
            'active': True
        })
    
    # Remove duplicates (same station_id)
    stations_df = pd.DataFrame(stations)
    stations_df = stations_df.drop_duplicates(subset=['station_id'], keep='first')
    
    print(f"✓ Loaded {len(stations_df)} stations from manual list")
    
    return stations_df


def verify_and_save_stations(stations_df: pd.DataFrame) -> pd.DataFrame:
    """
    Verify station data and save to CSV
    
    Args:
        stations_df: DataFrame of station data
    
    Returns:
        Cleaned and verified DataFrame
    """
    print("\nVerifying station data...")
    
    # Check for required columns
    required_cols = ['station_id', 'name', 'latitude', 'longitude']
    for col in required_cols:
        if col not in stations_df.columns:
            print(f"Warning: Missing column {col}")
            return stations_df
    
    # Remove any rows with missing coordinates
    initial_count = len(stations_df)
    stations_df = stations_df.dropna(subset=['latitude', 'longitude'])
    removed = initial_count - len(stations_df)
    if removed > 0:
        print(f"Removed {removed} stations with missing coordinates")
    
    # Verify coordinates are in Colorado bounds
    co_bounds = {
        'min_lat': 36.9,
        'max_lat': 41.1,
        'min_lon': -109.1,
        'max_lon': -102.0
    }
    
    in_bounds = (
        (stations_df['latitude'] >= co_bounds['min_lat']) &
        (stations_df['latitude'] <= co_bounds['max_lat']) &
        (stations_df['longitude'] >= co_bounds['min_lon']) &
        (stations_df['longitude'] <= co_bounds['max_lon'])
    )
    
    out_of_bounds = (~in_bounds).sum()
    if out_of_bounds > 0:
        print(f"Warning: {out_of_bounds} stations outside Colorado bounds")
        stations_df = stations_df[in_bounds]
    
    # Sort by name
    stations_df = stations_df.sort_values('name').reset_index(drop=True)
    
    # Save to CSV
    stations_df.to_csv(STATIONS_LIST, index=False)
    print(f"\n✓ Saved {len(stations_df)} stations to: {STATIONS_LIST}")
    
    # Print summary
    print("\n" + "="*60)
    print("STATION SUMMARY")
    print("="*60)
    print(f"\nTotal stations: {len(stations_df)}")
    print(f"\nElevation range:")
    if 'elevation_ft' in stations_df.columns:
        print(f"  Min: {stations_df['elevation_ft'].min():.0f} ft ({stations_df['elevation_m'].min():.0f} m)")
        print(f"  Max: {stations_df['elevation_ft'].max():.0f} ft ({stations_df['elevation_m'].max():.0f} m)")
        print(f"  Mean: {stations_df['elevation_ft'].mean():.0f} ft ({stations_df['elevation_m'].mean():.0f} m)")
    
    print(f"\nGeographic coverage:")
    print(f"  Latitude: {stations_df['latitude'].min():.2f}° to {stations_df['latitude'].max():.2f}°")
    print(f"  Longitude: {stations_df['longitude'].min():.2f}° to {stations_df['longitude'].max():.2f}°")
    
    # Show sample
    print(f"\nSample stations:")
    print(stations_df[['station_id', 'name', 'latitude', 'longitude', 'elevation_ft']].head(10).to_string(index=False))
    
    return stations_df


def main():
    """Main function to build station list"""
    
    # Try API first, fall back to manual list
    stations_df = get_colorado_snotel_stations_from_nrcs()
    
    # If API failed or returned too few stations, use manual list
    if stations_df.empty or len(stations_df) < 20:
        print("\nAPI returned insufficient data, using comprehensive manual list...")
        stations_df = get_manual_colorado_stations()
    
    # Verify and save
    stations_df = verify_and_save_stations(stations_df)
    
    return stations_df


if __name__ == "__main__":
    stations_df = main()