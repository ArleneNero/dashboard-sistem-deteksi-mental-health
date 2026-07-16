import plotly.graph_objects as go

try:
    fig = go.Figure(go.Pie(
        labels=["Masalah Keluarga", "Tekanan Akademik"],
        values=[132, 68],
        texttemplate="%{label}<br>%{percent:.1%}",
        textposition="inside",
        insidetextorientation="radial"
    ))
    print("Plotly Pie texttemplate configured successfully.")
except Exception as e:
    print(f"Error: {e}")
