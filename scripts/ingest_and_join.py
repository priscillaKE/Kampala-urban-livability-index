import os
import argparse
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt


def main(input_csv: str, shp: str, out_dir: str):
    # Read data
    if not os.path.exists(shp):
        raise FileNotFoundError(shp)
    if not os.path.exists(input_csv):
        raise FileNotFoundError(input_csv)

    adm2 = gpd.read_file(shp)
    print('ADM2 loaded:', adm2.shape)

    pts = pd.read_csv(input_csv)
    print('Sample points loaded:', pts.shape)
    # Create GeoDataFrame of points
    geometry = [Point(xy) for xy in zip(pts['lon'], pts['lat'])]
    pts_gdf = gpd.GeoDataFrame(pts, geometry=geometry, crs='EPSG:4326')

    # Ensure ADM2 is in WGS84 for spatial join
    if adm2.crs is None:
        adm2.set_crs(epsg=4326, inplace=True)
    else:
        adm2 = adm2.to_crs(epsg=4326)

    # Spatial join: which ADM2 contains each point
    joined = gpd.sjoin(pts_gdf, adm2[['ADM2_EN','geometry']], how='left', predicate='within')
    print('After join, rows:', joined.shape)

    # Aggregate counts per ADM2
    counts = joined.groupby('ADM2_EN').size().reset_index(name='school_count')
    print('Aggregated counts:', counts.shape)

    # Merge counts into adm2 polygons
    adm2_counts = adm2.merge(counts, on='ADM2_EN', how='left')
    adm2_counts['school_count'] = adm2_counts['school_count'].fillna(0).astype(int)

    # Prepare output dir
    os.makedirs(out_dir, exist_ok=True)

    # Save CSV and GeoJSON
    adm2_counts[['ADM2_EN','school_count']].to_csv(os.path.join(out_dir, 'schools_by_adm2.csv'), index=False)
    adm2_counts.to_file(os.path.join(out_dir, 'schools_by_adm2.geojson'), driver='GeoJSON')
    print('Saved processed school aggregation to', out_dir)

    # Plot choropleth of school counts
    os.makedirs('outputs', exist_ok=True)
    plt.switch_backend('Agg')
    ax = adm2_counts.plot(column='school_count', cmap='OrRd', figsize=(10,10), legend=True, edgecolor='black')
    ax.set_title('School counts per ADM2')
    plt.savefig('outputs/schools_count_choropleth.png', dpi=150, bbox_inches='tight')
    plt.close()

    # Plot points overlayed on boundaries
    ax = adm2.plot(color='lightgrey', edgecolor='black', figsize=(10,10))
    pts_gdf.plot(ax=ax, color='blue', markersize=30)
    plt.title('School points over ADM2 boundaries')
    plt.savefig('outputs/schools_points.png', dpi=150, bbox_inches='tight')
    plt.close()
    print('Saved outputs/schools_count_choropleth.png and outputs/schools_points.png')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ingest points CSV and spatial-join to ADM2 boundaries')
    parser.add_argument('--input', '-i', dest='input_csv', default='data/samples/schools.csv', help='Input CSV of points (must have lon,lat columns)')
    parser.add_argument('--shp', '-s', dest='shp', default='data/boundaries/uga_admbnda_adm2_ubos_20200824.shp', help='ADM2 shapefile path')
    parser.add_argument('--outdir', '-o', dest='out_dir', default=None, help='Output directory (overrides --name)')
    parser.add_argument('--name', '-n', dest='name', default='sample_schools', help='Dataset name; outputs saved to data/processed/<name> when --outdir not provided')
    args = parser.parse_args()
    # determine outdir
    if args.out_dir:
        outdir = args.out_dir
    else:
        outdir = os.path.join('data', 'processed', args.name)
    main(args.input_csv, args.shp, outdir)
