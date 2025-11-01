import os
import geopandas as gpd
import matplotlib.pyplot as plt

shp = r'data/boundaries/uga_admbnda_adm2_ubos_20200824.shp'
if not os.path.exists(shp):
    raise FileNotFoundError(shp)

gdf = gpd.read_file(shp)
print('Loaded ADM2:', gdf.shape)
print('Columns:', list(gdf.columns))

# Ensure we have a geographic CRS for centroid-based equal-area projection
if gdf.crs is None:
    print('Input has no CRS; assuming WGS84 (EPSG:4326)')
    gdf.set_crs(epsg=4326, inplace=True)

# Build a local Lambert Azimuthal Equal-Area projection centered on the data extent
centroid = gdf.geometry.unary_union.centroid
laea_crs = f"+proj=laea +lat_0={centroid.y} +lon_0={centroid.x} +datum=WGS84 +units=m +no_defs"
proj = gdf.to_crs(laea_crs)
proj['area_km2'] = proj.geometry.area / 1e6
gdf['area_km2'] = proj['area_km2']

print('Area stats (km2):')
print(gdf['area_km2'].describe())

# Show top 10 largest ADM2 by area
print('\nTop 10 ADM2 by area:')
print(gdf.nlargest(10, 'area_km2')[['ADM2_EN','area_km2']].to_string(index=False))

# Filter Kampala (try ADM2_EN first, else scan)
if 'ADM2_EN' in gdf.columns:
    kampala = gdf[gdf['ADM2_EN'].astype(str).str.contains('Kampala', case=False, na=False)]
else:
    kampala = gdf[gdf.apply(lambda r: r.astype(str).str.contains('Kampala', case=False, na=False).any(), axis=1)]

print('Kampala rows found:', len(kampala))

# Save processed GeoJSON
out_dir = 'data/processed'
os.makedirs(out_dir, exist_ok=True)
processed_path = os.path.join(out_dir, 'adm2_processed.geojson')
gdf.to_file(processed_path, driver='GeoJSON')
print('Saved processed GeoJSON to', processed_path)

# Produce a simple choropleth by area and save to outputs
os.makedirs('outputs', exist_ok=True)
plt.switch_backend('Agg')
ax = gdf.plot(column='area_km2', cmap='viridis', figsize=(10, 10), legend=True, edgecolor='black')
ax.set_title('ADM2 areas (km2)')
plt.savefig('outputs/adm2_area_choropleth.png', dpi=150, bbox_inches='tight')
plt.close()

# Also save a zoomed map for Kampala if present
if len(kampala):
    ax = gdf.plot(figsize=(8, 8), color='lightgrey', edgecolor='black')
    kampala.plot(ax=ax, color='red', edgecolor='black')
    minx, miny, maxx, maxy = kampala.total_bounds
    xpad = (maxx - minx) * 0.1 if (maxx - minx) != 0 else 0.01
    ypad = (maxy - miny) * 0.1 if (maxy - miny) != 0 else 0.01
    ax.set_xlim(minx - xpad, maxx + xpad)
    ax.set_ylim(miny - ypad, maxy + ypad)
    plt.savefig('outputs/kampala_zoom.png', dpi=150, bbox_inches='tight')
    plt.close()
    print('Saved outputs/kampala_zoom.png')

print('Saved outputs/adm2_area_choropleth.png')
