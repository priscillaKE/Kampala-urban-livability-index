"""Interactive dashboard for the Kampala Urban Livability Index."""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import folium
import geopandas as gpd
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.geospatial import aggregate_points_by_area
from src.index import calculate_livability_index


st.set_page_config(page_title="Kampala Urban Livability Index", layout="wide")


def render_index_workspace() -> None:
    st.header("Livability index")
    st.caption("Compare area-level indicators with transparent directions and weights.")

    use_demo = st.checkbox(
        "Use illustrative sample data",
        value=True,
        help="The included sample is for testing the workflow, not an official Kampala estimate.",
    )
    uploaded = st.file_uploader("Upload an area-level indicator CSV", type="csv")
    if uploaded is not None:
        data = pd.read_csv(uploaded)
        source_label = uploaded.name
    elif use_demo:
        data = pd.read_csv("data/samples/demo_area_indicators.csv")
        source_label = "Illustrative demo data"
    else:
        st.info("Upload a CSV to calculate an index.")
        return

    area_column = st.selectbox("Area identifier", options=list(data.columns), index=0)
    numeric_columns = [column for column in data.columns if column != area_column and pd.api.types.is_numeric_dtype(data[column])]
    if not numeric_columns:
        st.error("The CSV needs at least one numeric indicator column.")
        return

    indicators = st.multiselect("Indicators", options=numeric_columns, default=numeric_columns)
    if not indicators:
        st.warning("Select at least one indicator.")
        return

    st.subheader("Indicator assumptions")
    settings = st.columns(len(indicators))
    directions: dict[str, bool] = {}
    weights: dict[str, float] = {}
    for column, panel in zip(indicators, settings):
        with panel:
            directions[column] = st.checkbox(f"Higher is better: {column}", value=True)
            weights[column] = st.number_input(
                f"Weight: {column}", min_value=0.0, value=1.0, step=0.5, key=f"weight_{column}"
            )

    if sum(weights.values()) <= 0:
        st.error("At least one indicator weight must be greater than zero.")
        return

    result = calculate_livability_index(data, indicators, directions, weights)
    result = result.sort_values(["livability_rank", area_column])
    st.caption(f"Source: {source_label}. Scores are relative to the uploaded data.")

    metric_columns = st.columns(3)
    metric_columns[0].metric("Areas", len(result))
    metric_columns[1].metric("Top area", str(result.iloc[0][area_column]))
    metric_columns[2].metric("Top score", f"{result.iloc[0]['livability_score']:.2f}")

    left, right = st.columns([1.2, 1])
    with left:
        st.subheader("Ranking")
        st.dataframe(
            result[[area_column, "livability_score", "livability_rank", "data_completeness"]],
            use_container_width=True,
            hide_index=True,
        )
    with right:
        chart = px.bar(
            result,
            x="livability_score",
            y=area_column,
            orientation="h",
            range_x=[0, 100],
            labels={"livability_score": "Score", area_column: "Area"},
        )
        chart.update_layout(height=max(320, len(result) * 45), margin=dict(l=8, r=8, t=24, b=8))
        st.plotly_chart(chart, use_container_width=True)

    with st.expander("Indicator details"):
        st.dataframe(result, use_container_width=True, hide_index=True)
    st.download_button(
        "Download ranking CSV",
        result.to_csv(index=False),
        file_name="kampala_livability_ranking.csv",
        mime="text/csv",
    )


def render_map_workspace() -> None:
    st.header("Geospatial ingest")
    st.caption("Assign uploaded point records to administrative areas and inspect the result on a map.")

    use_sample = st.checkbox("Use sample school data", value=True)
    uploaded_file = st.file_uploader("Upload point CSV", type="csv", key="point_csv")
    shapefile = st.text_input(
        "Boundary shapefile",
        value="data/boundaries/uga_admbnda_adm2_ubos_20200824.shp",
    )
    if uploaded_file is not None:
        preview = pd.read_csv(uploaded_file)
        csv_path = None
    elif use_sample:
        preview = pd.read_csv("data/samples/schools.csv")
        csv_path = "data/samples/schools.csv"
    else:
        st.info("Upload a point CSV or enable the sample dataset.")
        return

    columns = list(preview.columns)
    lon_col = st.selectbox("Longitude column", columns, index=columns.index("lon") if "lon" in columns else 0)
    lat_col = st.selectbox("Latitude column", columns, index=columns.index("lat") if "lat" in columns else 0)
    label_col = st.selectbox("Label column", [""] + columns, index=1 if "name" in columns else 0)

    if st.button("Run spatial join", type="primary"):
        if not os.path.exists(shapefile):
            st.error(f"Boundary file not found: {shapefile}")
            return
        if uploaded_file is not None:
            temporary = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
            temporary.write(uploaded_file.getvalue())
            temporary.close()
            csv_path = temporary.name
        with st.spinner("Joining points to boundaries..."):
            areas, points = aggregate_points_by_area(csv_path, shapefile, lon_col, lat_col)

        st.success(f"Processed {len(points)} points across {len(areas)} areas.")
        st.dataframe(areas.drop(columns="geometry").sort_values("count", ascending=False).head(10), use_container_width=True, hide_index=True)
        center = [points.geometry.y.mean(), points.geometry.x.mean()]
        fmap = folium.Map(location=center, zoom_start=11)
        folium.GeoJson(areas.to_json(), name="Administrative areas").add_to(fmap)
        for _, row in points.iterrows():
            popup = str(row.get(label_col, "")) if label_col else ""
            folium.CircleMarker(
                location=(row.geometry.y, row.geometry.x),
                radius=5,
                color="#176b87",
                fill=True,
                popup=popup,
            ).add_to(fmap)
        st_folium(fmap, use_container_width=True, height=600)


st.title("Kampala Urban Livability Index")
st.caption("A transparent workspace for comparing documented indicators across Kampala areas.")
index_tab, map_tab = st.tabs(["Index workspace", "Geospatial ingest"])
with index_tab:
    render_index_workspace()
with map_tab:
    render_map_workspace()
