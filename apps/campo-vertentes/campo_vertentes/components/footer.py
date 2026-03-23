import solara


@solara.component
def Footer():
	with solara.Row(
		style={
			"background-color": "#2c3e50",
			"padding": "10px 20px",
			"justify-content": "center",
			"align-items": "center",
			"border-top": "1px solid #34495e",
			"border-radius": "0",
		}
	):
		solara.Text("© 2026 Geo3Café", style={"color": "#95a5a6"})
