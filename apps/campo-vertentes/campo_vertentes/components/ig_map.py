import ipyleaflet as leaflet
import solara

from ..styles import set_map_bg_color


# Classe personalizada para o mapa com configuração de layout
class Map(leaflet.Map):
	"""Mapa Leaflet customizado com configuração de layout."""

	def __init__(self, height="500px", controls=None, **kwargs):
		super().__init__(**kwargs)
		self.layout.height = height
		self.layout.width = "100%"

		if controls:
			self.controls = controls


@solara.component
def IGMap(
	center,
	on_center,
	zoom,
	on_zoom,
	controls,
	layers,
	height="500px",
	on_bounds=None,
	on_click=None,
	bg_color="#e0e0e0",
):
	"""
	Componente de mapa usando ipyleaflet com Solara.

	Args:
	    center: Centro do mapa [lat, lon]
	    on_center: Callback quando o centro muda
	    zoom: Nível de zoom
	    on_zoom: Callback quando o zoom muda
	    controls: Lista de controles do mapa
	    layers: Lista de camadas do mapa
	    height: Altura do mapa (padrão: "500px")
	    on_bounds: Callback quando os limites mudam
	    on_click: Callback quando o usuário interage com o mapa
	    bg_color: Cor de fundo do mapa (padrão: "#e0e0e0")
	"""

	# Definir cor de fundo específica via variável CSS

	def setup_interaction():
		if on_click is None:
			return

		widget = solara.get_widget(map_widget)

		widget.on_interaction(on_click)

		return lambda: widget.on_interaction(on_click, remove=True)

	solara.use_effect(setup_interaction, [])

	solara.HTML(unsafe_innerHTML=set_map_bg_color(bg_color))

	map_widget = Map.element(
		height=height,
		center=center,
		zoom=zoom,
		on_center=on_center,
		on_zoom=on_zoom,
		on_bounds=on_bounds,
		on_interaction=lambda **kwargs: print(kwargs),
		scroll_wheel_zoom=True,
		controls=controls,
		layers=layers,
	)

	# Container com fallback de cor de fundo
	with solara.Column(
		style={"background-color": bg_color, "height": height, "width": "100%"}
	):
		return map_widget
