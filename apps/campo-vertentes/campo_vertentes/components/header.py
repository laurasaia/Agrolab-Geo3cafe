import solara

from campo_vertentes.routes import ROUTES


@solara.component
def Header():
	route, routes = solara.use_route()

	solara.Title("Geo3Café")

	with solara.Row(
		style={
			"background-color": "#2c3e50",
			"padding": "10px 20px",
			"justify-content": "space-between",
			"align-items": "center",
			"border-bottom": "1px solid #34495e",
			"border-radius": "0",
		}
	):
		solara.Text(
			"Geo3Café",
			style={
				"font-weight": "bold",
				"font-size": "20px",
				"line-height": "1.1",
				"color": "#ecf0f1",
			},
		)

		with solara.Row(style={"background-color": "#2c3e50", "gap": "25px"}):
			for r in routes:
				route_config = ROUTES[r.path]
				with solara.Link(r):
					solara.Button(
						route_config["name"],
						icon_name=route_config["icon"],
						color="primary" if r == route else None,
					)
