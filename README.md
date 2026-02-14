# Avalanche Risk Model

Machine learning model to predict avalanche probability and size across Colorado. Built for Big Data Architecture (CSCI5214) course at CU Boulder.

## Project Overview

Combines historical avalanche data with terrain and weather features to predict natural avalanche risk:
- **Avalanche data:** 15,826 natural avalanches from Colorado Avalanche Information Center (CAIC)
- **Terrain features:** Elevation, slope, aspect from SRTM DEM data
- **Weather features:** Snow depth, temperature, SWE from 118 SNOTEL stations using inverse distance weighting

## Prerequisites

- Python 3.11
- Conda (recommended for macOS ARM)
- ~50 MB disk space (DEM file)
- Internet connection for SNOTEL API queries

## Setup

### Conda Environment (Recommended)
```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/avalanche-risk-model.git
cd avalanche-risk-model

# Create environment
conda create -n avalanche python=3.11 -c conda-forge -y
conda activate avalanche

# Install dependencies
conda install -c conda-forge richdem -y
pip install setuptools
pip install -r requirements.txt
```

### Virtual Environment (Alternative)
```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/avalanche-risk-model.git
cd avalanche-risk-model

# Create and activate venv
python -m venv venv
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

**Note:** richdem may fail on macOS ARM via pip - use conda method instead.

## Data Pipeline

### Step 1: Load and Clean CAIC Data ✅
```bash
python scripts/01_load_and_clean_caic.py
```

- Loads raw CAIC avalanche data
- Filters to natural/unknown triggers only
- Removes invalid coordinates and missing critical fields
- **Output:** `data/processed/caic_clean.csv` (15,826 observations)

### Step 2: Build SNOTEL Station List ✅
```bash
python scripts/build_snotel_stations.py
```

- Creates comprehensive list of 118 Colorado SNOTEL stations
- Includes station triplets, coordinates, elevations
- **Output:** `data/processed/snotel_stations.csv`

### Step 3: Download DEM ✅
```bash
python scripts/download_dem.py
```

- Downloads SRTM GL3 (90m) DEM for Colorado from OpenTopography
- Requires OpenTopography API key
- **Output:** `data/external/colorado_dem.tif` (~48 MB)

### Step 4: Extract Terrain Features ✅
```bash
python scripts/02_extract_terrain_dem.py
```

- Extracts elevation, slope, aspect from DEM for 6,080 unique locations
- Converts slope calculations to proper units (accounts for lat/lon → meters)
- **Runtime:** ~1 minute
- **Output:** `data/processed/terrain_cache.csv`

### Step 5: Fetch Weather Data 🔄
```bash
python scripts/03_fetch_weather.py
```

- Queries SNOTEL API for each avalanche date
- Uses 3-station inverse distance weighting (IDW) for spatial interpolation
- Fetches: snow depth, 24h snow change, SWE, temperature
- Caches results to minimize API calls
- **Runtime:** 3-5 hours
- **Output:** `data/processed/weather_cache.csv`

### Step 6: Combine Features ⏳
```bash
python scripts/04_combine_features.py
```

- Merges CAIC + terrain + weather data
- **Output:** `data/processed/positive_examples_enriched.csv` (15,826 rows with all features)

### Step 7: Generate Negative Examples ⏳

- Sample safe days (no avalanches) with similar terrain
- Create balanced dataset (~31,652 negative examples)
- **Output:** `data/processed/training_data.csv` (~47,478 total rows)

### Step 8: Train Model ⏳

- Train multi-output model (avalanche probability + size prediction)
- Evaluate on test set
- Save trained model

## Project Structure
```
avalanche-risk-model/
│
├── data/
│   ├── raw/                           # Original CAIC CSV (not in git)
│   ├── processed/                     # Processed datasets
│   │   ├── caic_clean.csv            # ✓ Cleaned avalanche data
│   │   ├── snotel_stations.csv       # ✓ SNOTEL station list
│   │   ├── terrain_cache.csv         # ✓ Terrain features
│   │   └── weather_cache.csv         # 🔄 Weather features (in progress)
│   └── external/
│       └── colorado_dem.tif          # ✓ DEM file (48 MB, not in git)
│
├── scripts/
│   ├── 01_load_and_clean_caic.py     # ✓ Data cleaning
│   ├── 02_extract_terrain_dem.py     # ✓ Terrain extraction
│   ├── 03_fetch_weather.py           # 🔄 Weather fetching
│   ├── build_snotel_stations.py      # ✓ Station list builder
│   ├── download_dem.py               # ✓ DEM downloader
│   └── utils/
│       ├── terrain_utils.py          # DEM processing functions
│       └── weather_utils.py          # SNOTEL query + IDW functions
│
├── notebooks/
│   └── 01_eda_caic_avalanches.ipynb  # ✓ Exploratory data analysis
│
├── .gitignore
├── README.md
└── requirements.txt
```

## Current Progress

- ✅ **Data collection:** CAIC avalanche data loaded and cleaned (15,826 obs)
- ✅ **EDA:** Comprehensive analysis of temporal, geographic, and avalanche patterns
- ✅ **SNOTEL stations:** 118 Colorado stations identified and cataloged
- ✅ **DEM download:** SRTM 90m elevation data acquired
- ✅ **Terrain extraction:** Elevation, slope, aspect computed for 6,080 locations
- 🔄 **Weather fetching:** SNOTEL data extraction in progress (3-5 hours runtime)
- ⏳ **Feature combination:** Pending weather completion
- ⏳ **Negative sampling:** Planned
- ⏳ **Model training:** Planned

## Dataset Statistics

| Metric | Value |
|--------|-------|
| Total avalanches | 15,826 (natural/unknown triggers) |
| Date range | 2016-02-06 to 2026-02-13 (10 years) |
| Unique locations | 6,080 coordinates |
| Unique dates | 1,661 days |
| CAIC regions | 10 forecast zones |
| SNOTEL stations | 118 across Colorado |
| Peak season | December - March |
| Avalanche sizes | D1.0 - D5.0 (mean: D1.74) |
| Elevation range | 1,515 - 4,385 m |
| Mean slope | 33° (avalanche terrain) |

## Key Technical Decisions

**Inverse Distance Weighting (IDW):**
- Uses 3 nearest SNOTEL stations per avalanche location
- Power parameter = 2 (inverse square)
- Handles sparse weather station coverage across Colorado mountains

**Terrain Extraction:**
- SRTM GL3 (90m resolution) balances accuracy and file size
- Slope calculated using Horn's method with proper lat/lon → meters conversion
- Aspect converted to both degrees (0-360°) and cardinal directions

**Data Filtering:**
- Only natural (N) and unknown (U) triggers included
- Human-triggered avalanches excluded (not relevant for forecasting)
- 98.6% aspect coverage from CAIC, supplemented by DEM calculations

## Known Issues

- **SNOTEL API:** Occasional timeouts - script has retry logic and caching
- **richdem on macOS ARM:** Must install via conda, not pip
- **DEM file size:** 48 MB - excluded from git (download script provided)
- **Weather data lag:** SNOTEL reports with 1-3 day delay

## Team Collaboration

**Before starting:**
1. Use conda environment (not venv) for consistency
2. Never commit: large data files, API keys, raw CAIC CSV
3. Run scripts from project root: `python scripts/script_name.py`
4. Check `.gitignore` before committing new files

**Git workflow:**
```bash
# Pull latest changes
git pull origin main

# Make your changes, then:
git add .
git commit -m "Description of changes"
git push origin main
```

## API Keys

**OpenTopography API:**
- Required for DEM download
- Get free key: https://opentopography.org/
- Set in `scripts/download_dem.py` or use environment variable:
```bash
  export OPENTOPO_API_KEY="your_key_here"
```

**SNOTEL/Metloom:**
- No API key required
- Uses NRCS public AWDB web service

## Resources

- [CAIC Avalanche Database](https://avalanche.state.co.us/)
- [SNOTEL Network](https://www.nrcs.usda.gov/wps/portal/wcc/home/snowClimateMonitoring/snowpack/)
- [OpenTopography](https://opentopography.org/)
- [Metloom Documentation](https://metloom.readthedocs.io/)

## License

Educational use only - CU Boulder CSCI5214 class project.