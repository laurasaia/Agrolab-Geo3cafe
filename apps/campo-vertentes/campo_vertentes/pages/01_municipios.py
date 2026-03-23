from typing import cast

import ipyleaflet as leaflet
import requests
import solara
from ipyleaflet import GeoJSON, TileLayer
from ipywidgets import HTML
from requests.exceptions import ConnectionError, HTTPError
from solara.alias import rv
from solara.lab import Task, use_task

from ..components import (
	DataLoadingWrapper,
	IGMap,
	Legenda,
	PointTimeSeriesChart,
	create_geoman_draw_control_with_button,
	create_map_legend_controls,
)
from ..config import CLASSES, GEOSERVER_URL, POINT_TIMESERIES_JSON
from ..stores import coffee_geo_data_store, geo_data_store, layers_store
from ..utils import find_geocode_by_name, find_name_by_geocode

# Setar roi inicial para Earth Engine Layers Store
roi = solara.reactive(None)

zoom = solara.reactive(11)
center = solara.reactive((-21.0, -44.0))  # Inicialização padrão
bounds = solara.reactive(None)
selected_district = solara.reactive(None)  # Será inicializado no componente

basemaps = [
	TileLayer.element(
		name="Satélite",
		url="http://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
		base=True,
	)
]
basecontrols = [
	leaflet.LayersControl.element(position="topright"),
	leaflet.ZoomControl.element(position="topleft"),
	leaflet.ScaleControl.element(position="bottomleft"),
]
layers = solara.reactive(basemaps)
controls = solara.reactive(basecontrols)
district_geo_layer = solara.reactive(None)
coffee_geo_layer = solara.reactive(None)
points_geo_layer = solara.reactive(None)
popup_layer = solara.reactive(None)
geoman_control = solara.reactive(None)
button_control = solara.reactive(None)

# Estados para marcador interativo
is_graph_mode = solara.reactive(False)
selected_location = solara.reactive(None)

# Dicionário para armazenar camadas API existentes (NDVI, EVI, etc.)
api_layers_cache = solara.reactive({})

# Estado global para controlar classes API selecionadas
selected_api_classes = solara.reactive([])
api_trigger = solara.reactive(0)

# Controles de legenda do mapa
is_layer_toogled = solara.reactive(False)
map_legend_control = solara.reactive(None)
legend_toggle_control = solara.reactive(None)
legend_visible = solara.reactive(True)


def toggle_layer(classe: str):
	"""Callback para alternar visibilidade da camada."""
	layers_store.toggle_layer(classe)
	is_layer_toogled.set(True)


def on_draw(target, action, geo_json):
	"""Captura quando um marcador é desenhado usando Geoman.

	Args:
	                                                                target: O controle GeomanDrawControl
	                                                                action: Tipo de ação ('create', 'edit', 'remove', etc)
	                                                                geo_json: Dados GeoJSON do marcador (pode ser lista ou dict)
	"""
	if action != "create":
		return

	# geo_json pode ser uma lista
	if isinstance(geo_json, list):
		if not geo_json:
			return
		geo_json = geo_json[0]  # Pegar primeiro item

	if not geo_json:
		return

	# Extrair coordenadas do marcador
	geometry = geo_json.get("geometry", {})
	if geometry.get("type") == "Point":
		coords = geometry.get("coordinates", [])  # [lon, lat]
		if len(coords) == 2:
			# Desativar modo de desenho e atualizar botão
			if geoman_control.value:
				geoman_control.value.current_mode = None
			if button_control.value and button_control.value.widget:
				button_control.value.widget.value = False  # Desativa toggle

			# Salvar nova localização (isso dispara criação do marcador)
			# selected_location.value = coords


def get_feature_info(lat, lon):
	# reprojeta ponto clicado
	# x31983, y31983 = to_31983(lon, lat)
	x31983, y31983 = lon, lat

	# Define tamanho padrão OpenLayers
	WIDTH = 101
	HEIGHT = 101
	X = 50
	Y = 50

	# Em vez de calcular bounds pela tela,
	# cria um bbox pequeno ao redor do ponto
	# por exemplo 200 metros pra cada lado
	# buffer = 100  # você pode ajustar
	buffer = 0.0005  # você pode ajustar

	minx = x31983 - buffer
	maxx = x31983 + buffer
	miny = y31983 - buffer
	maxy = y31983 + buffer

	bbox = f"{minx},{miny},{maxx},{maxy}"

	LAYERS = ",".join([str(c["layer"]) for c in CLASSES.values()])
	print("Visible layers for GetFeatureInfo:", LAYERS)

	# monta parâmetros
	params: dict[str, str | int] = {
		"SERVICE": "WMS",
		"VERSION": "1.1.1",
		"REQUEST": "GetFeatureInfo",
		"LAYERS": LAYERS,
		"QUERY_LAYERS": LAYERS,
		"INFO_FORMAT": "text/html",
		"FORMAT": "image/png",
		"FEATURE_COUNT": 50,
		"SRS": "EPSG:4326",
		"BBOX": bbox,
		"WIDTH": WIDTH,
		"HEIGHT": HEIGHT,
		"X": X,
		"Y": Y,
	}

	try:
		url = (
			f"{GEOSERVER_URL}/wms"
			+ "?"
			+ "&".join([f"{k}={v}" for k, v in params.items()])
		)
		print("GetFeatureInfo URL:", url)
		response = requests.get(f"{GEOSERVER_URL}/wms", params=params)
		response.raise_for_status()
		content = response.text
		print("GetFeatureInfo response:", content)
	except Exception as e:
		print(f"Erro ao buscar GetFeatureInfo: {e}")


@solara.component
def Page():
	# Estados unificados de loading e erro
	is_loading = solara.use_reactive(False)
	error_message = solara.use_reactive(None)
	data_ready = solara.use_reactive(False)

	# Estados locais
	api_error = solara.use_reactive(None)
	municipios_dict = solara.use_reactive({})

	# Definir título da página
	# solara.Title("Municípios")

	# Efeito único para carregar dados essenciais (municípios via WFS)
	def load_essential_data():
		"""Carrega dados essenciais: municípios via GeoServer/WFS."""
		is_loading.set(True)
		error_message.set(None)

		# Carregar dados de municípios
		geo_data_store.ensure_loaded(mode="wfs")

		# Verificar erro
		if geo_data_store.error:
			error_message.set(
				f"Erro ao carregar dados dos municípios: {geo_data_store.error}"
			)
			is_loading.set(False)
			data_ready.set(False)
			return

		# Aguardar carregamento
		if geo_data_store.loading:
			return

		# Verificar se foi carregado com sucesso
		if not geo_data_store.is_loaded():
			return

		# Dados carregados com sucesso
		gdf = geo_data_store.gdf
		if not gdf.empty:
			# Criar dicionário municipios_dict
			mun_dict = {
				geocodigo: row["nome"]
				for geocodigo, row in gdf.sort_values("nome").iterrows()
			}
			municipios_dict.set(mun_dict)

			# Configurar centro inicial
			center.value = geo_data_store.center

			# Inicializar selected_district se ainda não foi
			if selected_district.value is None and mun_dict:
				selected_district.value = list(mun_dict.keys())[0]

			print("✅ Dados de municípios carregados com sucesso")
			is_loading.set(False)
			data_ready.set(True)
		else:
			error_message.set("Dados de municípios vazios")
			is_loading.set(False)
			data_ready.set(False)

	solara.use_effect(load_essential_data, [geo_data_store.loading])

	def update_district():
		"""Atualiza o município selecionado (centro, geometrias base)."""
		if not data_ready.value or not selected_district.value:
			return

		try:
			error_message.set(None)
			gdf = geo_data_store.gdf

			district_data = gdf[gdf.index == selected_district.value]

			if district_data.empty:
				error_message.set("Município selecionado não encontrado")
				return

			# Buscar dados de café dinamicamente via Vector Tiles
			coffee_geo_data_store.load_coffee_as_vectortile(
				cd_mun=str(selected_district.value)
			)

			# Verificar se houve erro ao carregar dados de café
			if coffee_geo_data_store.error:
				error_message.set(coffee_geo_data_store.error)
				return

			district_center = district_data.geometry.centroid.iloc[0]
			district_geojson = district_data.__geo_interface__

			# Atualizar centro (zoom comentado para não forçar reset)
			center.value = [district_center.y, district_center.x]
			zoom.value = 11

			# Criar ou atualizar camada do município
			if district_geo_layer.value is None:
				district_geo_layer.value = GeoJSON(
					data=district_geojson,
					name="Municípios",
					style={
						"color": "black",
						"weight": 4,
						"fillOpacity": 0,
						"interactive": False,
					},
				)
			else:
				district_geo_layer.value.data = district_geojson

			# Criar ou atualizar camada de café para VectorTileLayer
			coffee_geo_layer.value = coffee_geo_data_store.vectortile_layer

			# Criar Geoman Draw Control com botão customizado se não existir
			if geoman_control.value is None:

				def on_toggle_draw_mode(is_active):
					"""Callback quando botão de desenho é ativado/desativado."""
					is_graph_mode.set(is_active)
					if is_active:
						geoman_control.value.clear_markers()

				geoman_draw, btn_control = create_geoman_draw_control_with_button(
					on_toggle_draw_mode
				)
				geoman_draw.on_draw(on_draw)
				geoman_control.set(geoman_draw)
				button_control.set(btn_control)
				controls.value = controls.value.copy() + [geoman_draw, btn_control]

		except Exception as e:
			error_message.set(f"Erro ao carregar dados da região: {str(e)}")
			print(f"Erro em update_district: {e}")
			import traceback

			traceback.print_exc()

	def update_overlay_layers():
		"""Atualiza apenas as camadas WMS baseado na visibilidade e ordem."""
		try:
			# Camadas base (município e café)
			base_layers = basemaps + [
				layer
				for layer in [district_geo_layer.value, coffee_geo_layer.value]
				if layer is not None
			]

			# Camadas WMS visíveis (já ordenadas pela store)
			visible_layers = layers_store.get_visible_layers() or []

			layers.value = visible_layers + base_layers
		except Exception as e:
			print(f"Erro em update_overlay_layers: {e}")
			import traceback

			traceback.print_exc()

	def update_map_legend():
		"""Atualiza a legenda do mapa para mostrar apenas a camada no topo."""
		if not is_layer_toogled.value:
			return
		try:
			# Buscar a primeira camada visível na ordem da store (topo da visualização)
			visible_order = layers_store.get_visible_order()
			top_layer_name = visible_order[0] if visible_order else None

			if not top_layer_name:
				# Sem camadas visíveis - remover legenda
				if (
					map_legend_control.value
					and map_legend_control.value in controls.value
				):
					new_controls = [
						c
						for c in controls.value
						if c != map_legend_control.value
						and c != legend_toggle_control.value
					]
					controls.value = new_controls
					map_legend_control.set(None)
					legend_toggle_control.set(None)
				return

			# Buscar informações da camada no topo
			from ..config import CLASSES

			classe_info = None

			if top_layer_name in CLASSES:
				classe_info = CLASSES[top_layer_name]

			if not classe_info:
				return

			# Criar HTML da legenda
			legend_items: list[dict[str, str]] = cast(
				list[dict[str, str]], classe_info["viz"]
			)

			if not legend_items:
				return

			legend_html = '<div style="background-color: white; padding: 10px; border-radius: 5px; border: 2px solid #333; max-width: 200px;">'
			legend_html += f'<h4 style="margin: 0 0 8px 0; font-size: 14px; color: #333;">{classe_info.get("label", top_layer_name)}</h4>'

			for item in legend_items:
				color = item["color"]
				label = item["label"]
				legend_html += '<div style="display: flex; align-items: center; margin-bottom: 4px; gap: 8px;">'
				legend_html += f'<div style="width: 20px; height: 20px; background-color: {color}; border: 1px solid black; flex-shrink: 0;"></div>'
				legend_html += (
					f'<span style="font-size: 12px; color: #000;">{label}</span>'
				)
				legend_html += "</div>"

			legend_html += "</div>"

			legend_widget = HTML(legend_html)

			# Função para alternar visibilidade
			def on_toggle_legend(visible):
				legend_visible.set(visible)
				if map_legend_control.value:
					if visible:
						legend_widget.layout.display = "block"
					else:
						legend_widget.layout.display = "none"

			# Criar controles de legenda
			new_legend_control, new_toggle_control = create_map_legend_controls(
				legend_widget, legend_visible, on_toggle_legend
			)

			# Remover controles antigos se existirem
			current_controls = [
				c
				for c in controls.value
				if c != map_legend_control.value and c != legend_toggle_control.value
			]

			# Adicionar novos controles
			map_legend_control.set(new_legend_control)
			legend_toggle_control.set(new_toggle_control)
			controls.value = current_controls + [new_legend_control, new_toggle_control]
		except Exception as e:
			print(f"Erro em update_map_legend: {e}")
			import traceback

			traceback.print_exc()

		finally:
			is_layer_toogled.set(False)

	# Atualizar legenda quando camada é alternada
	solara.use_effect(update_map_legend, [is_layer_toogled.value])

	# Atualizar município quando seleção muda
	solara.use_effect(update_district, [selected_district.value])

	# Atualizar camadas overlay quando ordem de visibilidade muda
	solara.use_effect(
		update_overlay_layers,
		[layers_store._visible_order.value, coffee_geo_layer.value],
	)

	# Função para buscar dados de série temporal de um ponto
	async def fetch_timeseries_data():
		"""Busca dados de série temporal para a localização selecionada."""
		if not selected_location.value:
			return None

		lon, lat = selected_location.value

		url = f"{POINT_TIMESERIES_JSON}?lng={lon}&lat={lat}"

		print(f"Buscando dados de pontos da API: {url}")

		try:
			response = requests.get(url)
			response.raise_for_status()
			result = response.json()
			return result
		except ConnectionError as e:
			api_error.set(
				f"Erro de conexão. Não foi possível conectar à base de dados. {e.response.status_code if e.response else ''}"
			)
		except HTTPError as e:
			match e.response.status_code:
				case 400:
					api_error.set(
						"Requisição inválida. Verifique as coordenadas fornecidas."
					)
				case 404:
					api_error.set(
						"Nenhum dado encontrado para as coordenadas fornecidas."
					)
				case 500:
					api_error.set("Erro no servidor ao processar a requisição.")
				case _:
					api_error.set(f"Erro desconhecido ao buscar dados: {str(e)}")

	# Criar task (será executada quando selected_location mudar)
	timeseries_task: Task = use_task(
		fetch_timeseries_data,
		dependencies=[selected_location.value],
	)

	def on_map_click(**kwargs):
		"""Callback quando o mapa é clicado - captura coordenadas com precisão total."""
		# Só processar cliques se estiver em modo gráfico
		if not is_graph_mode.value:
			return

		# Verificar se é um clique (type='click')
		if kwargs.get("type") != "click":
			return

		# Extrair coordenadas do evento com precisão total
		coordinates = kwargs.get("coordinates")
		if coordinates and len(coordinates) == 2:
			lat, lon = coordinates  # ipyleaflet retorna [lat, lon]

			# Desativar modo gráfico e botão
			is_graph_mode.set(False)
			if button_control.value and button_control.value.widget:
				button_control.value.widget.value = False

			# Salvar localização no formato [lon, lat]
			selected_location.value = [lon, lat]

			# Buscar valores do WMS GetFeatureInfo para as camadas visíveis
			# get_feature_info(lat, lon)

	with solara.Column() as main:
		# Mapa e controles
		with solara.ColumnsResponsive(12, medium=[2, 10]):
			with solara.Column():
				solara.Select(
					label="Selecione o Município:",
					value=find_name_by_geocode(
						geo_data_store.gdf, selected_district.value
					)
					if selected_district.value
					else None,
					values=list(municipios_dict.value.values())
					if municipios_dict.value
					else [],
					on_value=lambda nome: selected_district.set(
						find_geocode_by_name(geo_data_store.gdf, nome)
					),
				)

				Legenda(on_toggle_layer=toggle_layer)

			if district_geo_layer.value:
				with solara.Column(
					style={
						"position": "relative",
						"isolation": "isolate",
						"height": "100%",
						"min-height": "500px",
					}
				):
					IGMap(
						center=center.value,
						on_center=center.set,
						zoom=zoom.value,
						on_zoom=zoom.set,
						on_bounds=bounds.set,
						on_click=on_map_click,
						layers=layers.value,
						controls=controls.value,
						height="100%",
					)

					# Mostrar loading sobre o mapa se estiver carregando dados da API
					if timeseries_task.pending:
						with solara.Div(
							style={
								"position": "absolute",
								"top": "0",
								"left": "0",
								"width": "100%",
								"height": "100%",
								"background-color": "rgba(255, 255, 255, 0.7)",
								"display": "flex",
								"flex-direction": "column",
								"justify-content": "center",
								"align-items": "center",
								"z-index": "1000",
							}
						):
							rv.ProgressCircular(
								indeterminate=True, size=64, color="primary"
							)
			else:
				with solara.Column(
					style={"align-items": "center", "padding": "40px", "gap": "15px"}
				):
					rv.ProgressCircular(indeterminate=True, size=64, color="primary")
					solara.Text(
						"Carregando Mapa...",
						style={"font-size": "18px", "color": "#666"},
					)

		# Seção de gráfico de série temporal (fora do ColumnsResponsive)
		if timeseries_task.finished and timeseries_task.value:
			with solara.Card(style={"margin": "0 !important"}):
				# Extrair dados de série temporal
				result = timeseries_task.value
				if result.get("status") == "success":
					point_data_result = result.get("data", [])[
						0
					]  # Pegar primeiro ponto
					timeseries = point_data_result.get("timeseries", [])

					if timeseries:
						# Mostrar coordenadas do ponto
						metadata = point_data_result.get("metadata", {})
						coords = metadata.get("coordinates", [])
						if coords and len(coords) == 2:
							solara.Markdown(
								f"### Série Temporal do Ponto: {coords[1]:}, {coords[0]:}"
							)

						# Renderizar gráfico
						PointTimeSeriesChart(timeseries_data=timeseries)
					else:
						solara.Warning(
							"Não há dados de série temporal para este ponto."
						)
				else:
					solara.Error(
						f"Erro ao carregar dados: {result.get('message', 'Erro desconhecido')}"
					)

		elif timeseries_task.finished and api_error.value:
			with solara.Card(style={"margin": "0 !important"}):
				with solara.Column(align="center", style={"width": "100%"}):
					rv.Icon(children=["error_outline"], size=48, color="error")
					solara.Text(
						api_error.value,
						style={
							"font-size": "16px",
							"color": "#d32f2f",
							"margin-top": "10px",
						},
					)

		elif timeseries_task.pending:
			with solara.Card(style={"margin": "0 !important"}):
				with solara.Column(align="center", style={"width": "100%"}):
					rv.ProgressCircular(indeterminate=True, size=48, color="primary")
					solara.Text(
						"Carregando dados de série temporal...",
						style={
							"font-size": "16px",
							"color": "#666",
							"margin-top": "10px",
						},
					)

		else:
			with solara.Card(style={"margin": "0 !important"}):
				with solara.Column(align="center", style={"width": "100%"}):
					solara.Text(
						"Habilite o modo de seleção e marque um ponto dentro de uma cafeicultura.",
						style={"font-size": "14px", "color": "#999"},
					)

	return DataLoadingWrapper(
		is_loading=is_loading.value,
		error_message=error_message.value,
		data_ready=data_ready.value,
		on_retry=load_essential_data,
		children=[main],
	)
