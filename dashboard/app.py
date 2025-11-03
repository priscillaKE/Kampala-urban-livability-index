import streamlit as st
import tempfile
import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from streamlit_folium import st_folium
import folium

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
uploaded_file = st.sidebar.file_uploader('Or upload a CSV', type=['csv'])

# Column mapping UI
st.sidebar.markdown('### Column mapping')
lon_col = st.sidebar.text_input('Longitude column name', value='lon')
lat_col = st.sidebar.text_input('Latitude column name', value='lat')
label_col = st.sidebar.text_input('Label column (optional)', value='name')

shp_default = 'data/boundaries/uga_admbnda_adm2_ubos_20200824.shp'
shp = st.sidebar.text_input('ADM2 shapefile path', value=shp_default)

out_dir = 'data/processed'

def run_ingest(csv_path, shp_path, outdir, lon_col='lon', lat_col='lat'):
    adm2 = gpd.read_file(shp_path)
    pts = pd.read_csv(csv_path)
    # create geometry using mapped columns
    geometry = [Point(xy) for xy in zip(pts[lon_col], pts[lat_col])]
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
        adm2_counts, pts_gdf = run_ingest(csv_path, shp, out_dir, lon_col=lon_col, lat_col=lat_col)
    st.success('Ingest complete — saved to data/processed/ingest_adm2_counts.geojson')

    st.subheader('Top ADM2 by count')
    st.dataframe(adm2_counts[['ADM2_EN','count']].sort_values('count', ascending=False).head(10))

    st.subheader('Map (interactive)')
    # build folium map centered on points
    center = [pts_gdf.geometry.y.mean(), pts_gdf.geometry.x.mean()]
    m = folium.Map(location=center, zoom_start=11)
    folium.GeoJson(adm2_counts.to_crs(epsg=4326).to_json(), name='ADM2').add_to(m)
    for _, r in pts_gdf.iterrows():
        popup = r.get(label_col, '') if label_col in pts_gdf.columns else ''
        folium.CircleMarker(location=(r.geometry.y, r.geometry.x), radius=5, color='blue', fill=True, popup=popup).add_to(m)
    st_folium(m, width=900, height=600)

    st.markdown('Interactive map saved to `outputs/schools_map.html` if you ran the standalone visualizer.')

st.sidebar.markdown('''
### Notes
- CSV must contain `lon` and `lat` columns in decimal degrees.
- For other column names, edit the script or ask me to add column-mapping UI.
''')
