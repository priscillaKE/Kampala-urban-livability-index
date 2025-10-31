<<<<<<< HEAD
# Kampala Urban Livability & Opportunity Index

A data science project to rank Kampala neighborhoods/divisions based on a composite index of affordability, opportunity, and quality of life, with interactive, user-personalized dashboards.

## Features

- **Data Acquisition:** Ingest data from diverse sources (property prices, job listings, green space, amenities, safety, etc.) relevant to Kampala.
- **Geospatial Analysis:** Clean, process, and merge datasets using geospatial units (divisions, parishes, or neighborhoods).
- **Composite Index:** Normalize and combine factors with user-defined weights for a personalized livability score.
- **Machine Learning:** Cluster neighborhoods and detect "hidden gem" areas.
- **Visualization:** Interactive dashboard (Streamlit) with maps, rankings, and dynamic charts.

## Project Structure

```
kampala-urban-livability-index/
├── data/               # Raw and processed datasets
├── notebooks/          # Jupyter notebooks for EDA and prototyping
├── src/                # Python modules (ETL, feature engineering, modeling)
├── dashboard/          # Streamlit app code
├── requirements.txt    # Python dependencies
├── README.md           # Project overview & instructions
└── LICENSE             # License file (MIT by default)
```

## Getting Started

1. **Clone the repository:**
   ```bash
   git clone https://github.com/priscillaKE/kampala-urban-livability-index.git
   cd kampala-urban-livability-index
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the dashboard app:**
   ```bash
   streamlit run dashboard/app.py
   ```

## Data Sources (Suggestions)

- **Affordability:** Local property listing sites (Lamudi, Jumia House, Property24) or government housing data.
- **Opportunity:** Job listing platforms (BrighterMonday), Uganda Bureau of Statistics (UBOS) for income/unemployment.
- **Quality of Life:** Green space and amenities from OpenStreetMap (via OSMnx), safety data from KCCA or open police data.

## Next Steps

1. Acquire and clean boundary shapefiles for Kampala divisions/neighborhoods.
2. Ingest and process one data source (e.g., parks or property prices).
3. Prototype geospatial joining and visualization in a Jupyter notebook.
4. Build out the composite index and Streamlit dashboard.

## License

MIT License.

---

*This project is for learning and portfolio purposes. Data accuracy may vary depending on available sources.*
=======
# Kampala-urban-livability-index
A data science project to rank Kampala neighbourhoods on affordability, opportunity, and quality of life
<<<<<<< HEAD
>>>>>>> a7be4e66635c1eb2ae8d1a1866b45c1607ab26d3
=======
# Kampala Urban Livability & Opportunity Index

A data science project to rank Kampala neighborhoods/divisions based on a composite index of affordability, opportunity, and quality of life, with interactive, user-personalized dashboards.

## Features

- **Data Acquisition:** Ingest data from diverse sources (property prices, job listings, green space, amenities, safety, etc.) relevant to Kampala.
- **Geospatial Analysis:** Clean, process, and merge datasets using geospatial units (divisions, parishes, or neighborhoods).
- **Composite Index:** Normalize and combine factors with user-defined weights for a personalized livability score.
- **Machine Learning:** Cluster neighborhoods and detect "hidden gem" areas.
- **Visualization:** Interactive dashboard (Streamlit) with maps, rankings, and dynamic charts.

## Project Structure

```
kampala-urban-livability-index/
├── data/               # Raw and processed datasets
├── notebooks/          # Jupyter notebooks for EDA and prototyping
├── src/                # Python modules (ETL, feature engineering, modeling)
├── dashboard/          # Streamlit app code
├── requirements.txt    # Python dependencies
├── README.md           # Project overview & instructions
└── LICENSE             # License file (MIT by default)
```

## Getting Started

1. **Clone the repository:**
   ```bash
   git clone https://github.com/priscillaKE/kampala-urban-livability-index.git
   cd kampala-urban-livability-index
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the dashboard app:**
   ```bash
   streamlit run dashboard/app.py
   ```

## Data Sources (Suggestions)

- **Affordability:** Local property listing sites (Lamudi, Jumia House, Property24) or government housing data.
- **Opportunity:** Job listing platforms (BrighterMonday), Uganda Bureau of Statistics (UBOS) for income/unemployment.
- **Quality of Life:** Green space and amenities from OpenStreetMap (via OSMnx), safety data from KCCA or open police data.

## Next Steps

1. Acquire and clean boundary shapefiles for Kampala divisions/neighborhoods.
2. Ingest and process one data source (e.g., parks or property prices).
3. Prototype geospatial joining and visualization in a Jupyter notebook.
4. Build out the composite index and Streamlit dashboard.

## License

MIT License.

---


>>>>>>> d8dab9c066b280b1f41e8edeb35ef6dc97578f8d
