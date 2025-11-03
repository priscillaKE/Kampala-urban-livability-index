import streamlit as st
import tempfile
import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

st.set_page_config(layout='wide', page_title='Kampala Urban Livability - Prototype')
st.title('Kampala Urban Livability — Prototype Ingest & Map')

st.markdown(
    """
    This lightweight prototype demonstrates ingesting a point CSV (lon/lat), spatially joining to ADM2 boundaries, and visualizing results.

    Usage:
    - Upload a CSV with `lon` and `lat` columns, or use the sample `data/samples/schools.csv`.
    - Click `Run ingest` to perform a spatial join (ADM2 must be present at `data/boundaries/...`).
    """
)

use_sample = st.sidebar.checkbox('Use sample CSV (data/samples/schools.csv)', value=True)
uploaded_file = st.sidebar.file_uploader('Or upload a CSV with lon,lat columns', type=['csv'])

shp_default = 'data/boundaries/uga_admbnda_adm2_ubos_20200824.shp'
shp = st.sidebar.text_input('ADM2 shapefile path', value=shp_default)

out_dir = 'data/processed'

def run_ingest(csv_path, shp_path, outdir):
    adm2 = gpd.read_file(shp_path)
    pts = pd.read_csv(csv_path)
    geometry = [Point(xy) for xy in zip(pts['lon'], pts['lat'])]
    pts_gdf = gpd.GeoDataFrame(pts, geometry=geometry, crs='EPSG:4326')
    if adm2.crs is None:
        adm2.set_crs(epsg=4326, inplace=True)
    else:
        adm2 = adm2.to_crs(epsg=4326)
    joined = gpd.sjoin(pts_gdf, adm2[['ADM2_EN','geometry']], how='left', predicate='within')
    counts = joined.groupby('ADM2_EN').size().reset_index(name='count')
    adm2_counts = adm2.merge(counts, on='ADM2_EN', how='left')
    adm2_counts['count'] = adm2_counts['count'].fillna(0).astype(int)
    os.makedirs(outdir, exist_ok=True)
    adm2_counts.to_file(os.path.join(outdir, 'ingest_adm2_counts.geojson'), driver='GeoJSON')
    return adm2_counts, pts_gdf

if st.button('Run ingest'):
    if use_sample and uploaded_file is None:
        csv_path = 'data/samples/schools.csv'
    elif uploaded_file is not None:
        tf = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
        tf.write(uploaded_file.read())
        tf.close()
        csv_path = tf.name
    else:
        st.error('No CSV provided. Either enable sample or upload a CSV.')
        st.stop()

    if not os.path.exists(shp):
        st.error(f'ADM2 shapefile not found at {shp}')
        st.stop()

    with st.spinner('Running spatial join...'):
        adm2_counts, pts_gdf = run_ingest(csv_path, shp, out_dir)
    st.success('Ingest complete — saved to data/processed/ingest_adm2_counts.geojson')

    st.subheader('Top ADM2 by count')
    st.dataframe(adm2_counts[['ADM2_EN','count']].sort_values('count', ascending=False).head(10))

    st.subheader('Map (static)')
    st.map(pts_gdf[['lat','lon']])

    st.markdown('To generate an interactive map (Folium), run `scripts/visualize_folium.py` or open `outputs/schools_map.html`.')

st.sidebar.markdown('''
### Notes
- CSV must contain `lon` and `lat` columns in decimal degrees.
- For other column names, edit the script or ask me to add column-mapping UI.
''')
