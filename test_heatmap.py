import plotly.graph_objects as go

try:
    labels_x = ["Pertolongan<br>Segera", "Curhat<br>Ringan", "Tidak<br>Relevan"]
    labels_y = ["Pertolongan Segera", "Curhat Ringan", "Tidak Relevan"]
    z = [[5, 6, 0],
         [7, 79, 1],
         [0, 1, 1]]
    
    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=labels_x,
        y=labels_y,
        colorscale=[[0, "#FFFDF9"], [0.1, "#EDF8F2"], [1.0, "#38B000"]],
        showscale=True,
        text=[[str(val) for val in row] for row in z],
        texttemplate="%{text}",
        textfont={"family": "JetBrains Mono", "size": 14, "color": "#2A2E45"}
    ))
    fig.update_layout(
        title="Confusion Matrix — Test Set (Accuracy = 0.85)",
        xaxis_title="Predicted Label",
        yaxis_title="Actual Label"
    )
    print("Plotly Heatmap configured successfully.")
except Exception as e:
    print(f"Error: {e}")
