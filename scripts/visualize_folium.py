import argparse
import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import folium


def main(points_csv: str, shp: str, out_html: str = 'outputs/schools_map.html'):
    if not os.path.exists(points_csv):
        raise FileNotFoundError(points_csv)
    if not os.path.exists(shp):
        raise FileNotFoundError(shp)

    adm2 = gpd.read_file(shp)
    pts = pd.read_csv(points_csv)
    pts_gdf = gpd.GeoDataFrame(pts, geometry=[Point(xy) for xy in zip(pts.lon, pts.lat)], crs='EPSG:4326')

    # Center map on the dataset centroid
    center = [pts.lat.mean(), pts.lon.mean()]
    m = folium.Map(location=center, zoom_start=10)

    # Add ADM2 boundaries (convert datetimes to strings so JSON is serializable)
    adm2_json = adm2.to_crs(epsg=4326).copy()
    for c in adm2_json.select_dtypes(include=['datetime', 'datetimetz']):
        adm2_json[c] = adm2_json[c].astype(str)
    folium.GeoJson(adm2_json.to_json(), name='ADM2').add_to(m)

    # Add points
    for _, row in pts_gdf.iterrows():
        popup = folium.Popup(f"{row.get('name','')} ({row.get('type','')})", parse_html=True)
        folium.CircleMarker(location=(row.lat, row.lon), radius=6, color='blue', fill=True, popup=popup).add_to(m)

    os.makedirs(os.path.dirname(out_html) or '.', exist_ok=True)
    m.save(out_html)
    print('Saved interactive map to', out_html)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create interactive Folium map from points and ADM2 shapefile')
    parser.add_argument('--points', '-p', dest='points_csv', default='data/samples/schools.csv', help='Points CSV (lon,lat columns)')
    parser.add_argument('--shp', '-s', dest='shp', default='data/boundaries/uga_admbnda_adm2_ubos_20200824.shp', help='ADM2 shapefile')
    parser.add_argument('--out', '-o', dest='out_html', default='outputs/schools_map.html', help='Output HTML file')
    args = parser.parse_args()
    main(args.points_csv, args.shp, args.out_html)
