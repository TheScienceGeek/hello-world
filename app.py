import streamlit as st
import pandas as pd
import ezdxf
from shapely.geometry import Polygon
from io import BytesIO

def is_rectangle(coords):
    if len(coords) != 5:
        return False
    polygon = Polygon(coords)
    return polygon.is_valid and polygon.is_rectangle

def extract_panels_from_dxf(file):
    doc = ezdxf.read(file)
    msp = doc.modelspace()

    panels = []
    panel_count = 0

    for entity in msp:
        if entity.dxftype() == 'LWPOLYLINE':
            points = [(point[0], point[1]) for point in entity.get_points()]
            if len(points) == 4:
                points.append(points[0])
            if is_rectangle(points):
                panel_count += 1
                x_coords = [p[0] for p in points[:-1]]
                y_coords = [p[1] for p in points[:-1]]
                width = max(x_coords) - min(x_coords)
                height = max(y_coords) - min(y_coords)
                panels.append({
                    "Panel": f"Panel {panel_count}",
                    "Width (mm)": round(width, 2),
                    "Height (mm)": round(height, 2),
                    "Qty": 1,
                    "Material": "MDF",
                    "Thickness": "18mm"
                })

    return pd.DataFrame(panels)

# Streamlit UI
st.title("2D DXF to Cut List Generator")
st.write("Upload a DXF file with rectangular furniture panels.")

uploaded_file = st.file_uploader("Upload DXF File", type=["dxf"])

if uploaded_file:
    try:
        cutlist_df = extract_panels_from_dxf(uploaded_file)
        st.success("Cut list generated!")
        st.dataframe(cutlist_df)

        # Download button
        csv = cutlist_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Cut List as CSV",
            data=csv,
            file_name="cutlist.csv",
            mime="text/csv",
        )
    except Exception as e:
        st.error(f"Error processing DXF: {e}")
