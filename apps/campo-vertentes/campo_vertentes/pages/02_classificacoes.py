import ipyleaflet as leaflet
import solara
from ipyleaflet import GeoJSON, TileLayer
from solara.alias import rv

from ..components import (
	DataLoadingWrapper,
	IGMap,
	ModelPerformanceByMetric,
	ModelPerformanceByModel,
	ModelPerformanceTable,
)
from ..config import BS_COFFEE_YIELD_CLASSES, WMTS_TEMPLATE_URL
from ..stores import coffee_geo_data_store, geo_data_store

models_list = list(BS_COFFEE_YIELD_CLASSES.keys())  # constante, sem estado

basemaps = [
	TileLayer.element(
		name="Esri World Imagery",
		url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
		base=True,
	),
]
basecontrols = [
	leaflet.LayersControl.element(position="topright"),
	leaflet.ZoomControl.element(position="topleft"),
	leaflet.ScaleControl.element(position="bottomleft"),
	leaflet.AttributionControl.element(position="bottomright"),
]
# ^ .element(...) = "receita" declarativa, não widget real ainda. Seguro no módulo.


@solara.component
def ModelComparionColumn(
	side,
	selected_model_left, selected_model_right,
	opacity_left, opacity_right,
	on_model_change_cb, on_opacity_change_cb,
):
	with solara.Column(style={"gap": "10px"}):
		current_value = selected_model_left.value if side == "left" else selected_model_right.value
		other_value = selected_model_right.value if side == "left" else selected_model_left.value

		solara.Text(
			"Base" if side == "left" else "Comparação",
			style={"font-weight": "600", "font-size": "14px", "color": "#495057"},
		)

		with solara.Div(style={
			"display": "flex", "flex-wrap": "wrap", "gap": "8px",
			"justify-content": "center", "align-items": "center",
		}):
			for k in models_list:
				is_disabled = k == other_value
				is_selected = k == current_value
				solara.Button(
					label=BS_COFFEE_YIELD_CLASSES[k]["label"],
					on_click=lambda model_id=k: on_model_change_cb(side, model_id) if not is_disabled else None,
					disabled=is_disabled,
					color=BS_COFFEE_YIELD_CLASSES[k]["color"] if is_selected else None,
					outlined=not is_selected,
					style={"flex": "1 1 auto", "min-width": "120px", "max-width": "200px", "text-transform": "none"},
				)

		solara.SliderFloat(
			label="Opacidade",
			value=opacity_left.value if side == "left" else opacity_right.value,
			on_value=lambda v: on_opacity_change_cb(side, v),
			min=0.0, max=1.0, step=0.1,
		)


@solara.component
def PageHeader():
	with solara.Card(style={"margin": "0 !important"}):
		with solara.Column(style={"gap": "15px"}):
			with solara.Row(justify="space-between", style={"align-items": "center"}):
				solara.Text("Bom Sucesso", style={"font-size": "24px", "font-weight": "bold"})
				solara.Text("Ano: 2022", style={"font-size": "16px", "color": "#666"})

			solara.Markdown(
				"""
                No QGIS foi gerado um conjunto amostral com 5 mil pontos aleatórios sobre a área do município de Bom Sucesso,
                sendo 2500 pontos para cada uma das classes "Não Café" e "Café". Esse conjunto serviu de base para a criação
                das amostras das séries temporais utilizadas no treinamento dos modelos, que foram baseados em dados de imagens
                Sentinel-2 (obtidas pelo <a href="https://data.inpe.br/bdc/en/home-page-2/", target="_blank">Brazil Data Cube</a>) dos anos de 2018 a 2022.
                """,
				style={"color": "#495057", "font-size": "14px", "line-height": "1.6"},
			)


@solara.component
def ModelComparisonHeader(
	selected_model_left, selected_model_right,
	opacity_left, opacity_right,
	on_model_change_cb, on_opacity_change_cb, on_swap_cb,
):
	with solara.Card(style={"margin": "0 !important", "height": "100%"}):
		with solara.Column(style={"gap": "10px"}):
			with solara.ColumnsResponsive(
				12, medium=[5, 2, 5], large=12,
				style={"align-items": "center", "height": "100%", "width": "100%"},
			):
				ModelComparionColumn(
					side="left",
					selected_model_left=selected_model_left, selected_model_right=selected_model_right,
					opacity_left=opacity_left, opacity_right=opacity_right,
					on_model_change_cb=on_model_change_cb, on_opacity_change_cb=on_opacity_change_cb,
				)

				with solara.Column(align="center", style={"justify-content": "center"}):
					solara.Button(
						label="", icon_name="swap_horiz", on_click=on_swap_cb,
						color="primary", text=False, icon=True,
					)
					solara.Text("Inverter", style={"font-size": "11px", "text-align": "center", "color": "#666"})

				ModelComparionColumn(
					side="right",
					selected_model_left=selected_model_left, selected_model_right=selected_model_right,
					opacity_left=opacity_left, opacity_right=opacity_right,
					on_model_change_cb=on_model_change_cb, on_opacity_change_cb=on_opacity_change_cb,
				)


@solara.component
def GridRow(title: str = "Row Title"):
	with solara.Card() as card:
		with solara.Row(style={"align-items": "center"}):
			with solara.Column(style={"padding": "0 10px", "cursor": "move"}):
				rv.Icon(children=["drag_handle"], size=24, style={"color": "#666"})
			with solara.Column(style={"flex": "1"}):
				solara.Text(title, style={"font-weight": "600", "font-size": "18px"})
				solara.FloatSlider(min=0, max=1, step=0.1, value=0.5, label="Threshold")
	return card


@solara.component
def DraggableGrid():
	initial_layout = [
		{"h": 3, "i": "0", "moved": False, "w": 12, "x": 0, "y": 0},
		{"h": 3, "i": "1", "moved": False, "w": 12, "x": 0, "y": 1},
	]
	layout = solara.use_reactive(initial_layout)

	def on_grid_layout(new_layout):
		layout.set(new_layout)

	return solara.GridDraggable(
		grid_layout=layout.value,
		on_grid_layout=on_grid_layout,
		resizable=False,
		draggable=True,
		items=[GridRow(title=i["label"]) for i in BS_COFFEE_YIELD_CLASSES.values()],
	)


@solara.component
def ModelsInfo():
	with solara.ColumnsResponsive(12, medium=[6, 6]):
		with solara.Column(style={"gap": "10px"}):
			solara.Text("📊 Sobre os Modelos", style={"font-weight": "600", "font-size": "14px", "margin-bottom": "5px"})
			for model_id, config in BS_COFFEE_YIELD_CLASSES.items():
				with solara.Card(style={"padding": "10px", "border-left": f"3px solid {config['color']}", "background": "white"}):
					solara.Text(f"{config['name']}: ", style={"font-weight": "600", "font-size": "13px", "margin-bottom": "5px"})
					solara.Text(config["description"], style={"font-size": "12px", "color": "#666", "line-height": "1.4"})
					with solara.Row(style={"gap": "10px", "margin-top": "5px"}):
						solara.Text(f"Período: {config['timespan']}", style={"font-size": "11px", "color": "#999"})
						solara.Text(f"Bandas: {', '.join(config['bands'])}", style={"font-size": "11px", "color": "#999"})

		with solara.Column(style={"gap": "10px"}):
			solara.Text("📈 Sobre as Métricas", style={"font-weight": "600", "font-size": "14px", "margin-bottom": "5px"})
			metrics_info = {
				"Acurácia": {"desc": "Proporção de predições corretas em relação ao total de predições. Quanto maior, melhor.", "color": "#4CAF50"},
				"IoU": {"desc": "Intersection over Union - quantifica o grau de sobreposição entre as regiões preditas e ground truth. Fórmula: IoU = Área de Interseção / Área de União", "color": "#2196F3"},
				"Dice": {"desc": "Coeficiente Dice (F1 score) - avalia a similaridade entre máscaras. Fórmula: Dice = (2 × Interseção) / (Predito + Ground Truth)", "color": "#FF9800"},
			}
			for metric_name, info in metrics_info.items():
				with solara.Card(style={"padding": "10px", "border-left": f"3px solid {info['color']}", "background": "white"}):
					solara.Text(f"{metric_name}: ", style={"font-weight": "600", "font-size": "13px", "margin-bottom": "5px"})
					solara.Text(info["desc"], style={"font-size": "12px", "color": "#666", "line-height": "1.4"})


@solara.component
def Page():
	# --- Estado por sessão ---
	zoom = solara.use_reactive(11)
	center = solara.use_reactive((-21.0, -44.0))
	bounds = solara.use_reactive(None)
	selected_district = solara.use_reactive("3108008")

	selected_model_left = solara.use_reactive(models_list[0])
	selected_model_right = solara.use_reactive(models_list[1])
	layer_left = solara.use_reactive(None)
	opacity_left = solara.use_reactive(1)
	layer_right = solara.use_reactive(None)
	opacity_right = solara.use_reactive(1)
	models_layers = solara.use_reactive(None)

	layers = solara.use_reactive(basemaps)
	controls = solara.use_reactive(basecontrols)
	district_geo_layer = solara.use_reactive(None)
	coffee_geo_layer = solara.use_reactive(None)

	is_loading = solara.use_reactive(False)
	error_message = solara.use_reactive(None)
	data_ready = solara.use_reactive(False)

	show_info = solara.use_reactive(False)
	view_mode = solara.use_reactive("graficos")

	# --- Funções que dependem de reactive: closures locais ---
	def load_model_layer(model_id: str) -> leaflet.TileLayer:
		# TODO: Refatorar para VectorTileLayer ao invés de TileLayer
		print(f"🚀 Carregando camada do modelo: {model_id}")
		wfs_layer_name = str(BS_COFFEE_YIELD_CLASSES[model_id]["wfs_layer"])
		url = WMTS_TEMPLATE_URL.replace("<LAYER_NAME>", wfs_layer_name).replace("<TILE_FORMAT>", "image/png")
		model_layer = leaflet.TileLayer(url=url, name=f"Modelo: {BS_COFFEE_YIELD_CLASSES[model_id]['label']}", tile_size=256)

		if model_id == selected_model_left.value:
			model_layer.opacity = opacity_left.value
			layer_left.set(model_layer)
			if models_layers.value:
				models_layers.value = [models_layers.value[0], model_layer]
		else:
			model_layer.opacity = opacity_right.value
			layer_right.set(model_layer)
			if models_layers.value:
				models_layers.value = [model_layer, models_layers.value[1]]

		if district_geo_layer.value and coffee_geo_layer.value and models_layers.value:
			layers.value = basemaps + [
				models_layers.value[1], models_layers.value[0],
				district_geo_layer.value, coffee_geo_layer.value,
			]

		return model_layer

	def swap_models():
		temp_id = selected_model_left.value
		selected_model_left.value = selected_model_right.value
		selected_model_right.value = temp_id

		temp_layer = layer_left.value
		layer_left.value = layer_right.value
		layer_right.value = temp_layer

		temp_opacity = opacity_left.value
		opacity_left.value = opacity_right.value
		opacity_right.value = temp_opacity

		if models_layers.value and len(models_layers.value) == 2:
			models_layers.value = models_layers.value[::-1]
			models_layers.value[0].opacity = opacity_right.value
			models_layers.value[1].opacity = opacity_left.value
			layers.value = basemaps + [
				models_layers.value[1], models_layers.value[0],
				district_geo_layer.value, coffee_geo_layer.value,
			]

	def update_layer_opacity(layer_side: str, opacity: float):
		if layer_side == "left":
			models_layers.value[1].opacity = opacity
			opacity_left.set(opacity)
		elif layer_side == "right":
			models_layers.value[0].opacity = opacity
			opacity_right.set(opacity)

	def on_model_change(side: str, model_id: str):
		if side == "left":
			selected_model_left.set(model_id)
		else:
			selected_model_right.set(model_id)
		load_model_layer(model_id)

	def on_opacity_change(side: str, v: float):
		update_layer_opacity(side, v)

	def on_load():
		is_loading.set(True)
		error_message.set(None)

		geo_data_store.ensure_loaded(mode="wfs")

		if geo_data_store.error:
			error_message.set(f"Erro ao carregar dados dos municípios: {geo_data_store.error}")
			is_loading.set(False)
			data_ready.set(False)
			return

		if geo_data_store.loading:
			return

		if not geo_data_store.is_loaded():
			return

		gdf = geo_data_store.gdf

		if not gdf.empty:
			center.value = geo_data_store.center
			print("✅ Dados de municípios carregados com sucesso. Carregando camada de Café...")

			try:
				district_data = gdf[gdf.index == selected_district.value]
				if district_data.empty:
					error_message.set("Município selecionado não encontrado")
					return

				coffee_geo_data_store.load_coffee_as_vectortile(cd_mun=str(selected_district.value))

				if coffee_geo_data_store.error:
					error_message.set(coffee_geo_data_store.error)
					is_loading.set(False)
					data_ready.set(False)
					return

				district_center = district_data.geometry.centroid.iloc[0]
				district_geojson = district_data.__geo_interface__

				center.value = [district_center.y, district_center.x]
				zoom.value = 11

				if district_geo_layer.value is None:
					district_geo_layer.value = GeoJSON(
						data=district_geojson, name="Municípios",
						style={"color": "black", "weight": 4, "fillOpacity": 0},
					)
				else:
					district_geo_layer.value.data = district_geojson

				params = coffee_geo_data_store.vectortile_params
				if params:
					coffee_geo_layer.value = leaflet.VectorTileLayer(**params)

				left_layer = load_model_layer(selected_model_left.value)
				right_layer = load_model_layer(selected_model_right.value)

				models_layers.value = [right_layer, left_layer]
				layers.value = basemaps + [
					left_layer, right_layer, district_geo_layer.value, coffee_geo_layer.value,
				]

			except Exception as e:
				error_message.set(f"Erro ao carregar dados de café: {str(e)}")
				is_loading.set(False)
				data_ready.set(False)
				return

			is_loading.set(False)
			data_ready.set(True)
		else:
			error_message.set("Dados de municípios vazios")
			is_loading.set(False)
			data_ready.set(False)

	solara.use_effect(on_load, [])

	with solara.Column(style={"flex": "1"}) as main:
		PageHeader()

		with solara.ColumnsResponsive(12, large=[4, 8], xlarge=[3, 9]):
			ModelComparisonHeader(
				selected_model_left=selected_model_left, selected_model_right=selected_model_right,
				opacity_left=opacity_left, opacity_right=opacity_right,
				on_model_change_cb=on_model_change, on_opacity_change_cb=on_opacity_change,
				on_swap_cb=swap_models,
			)

			with solara.Column(style={"isolation": "isolate", "height": "100%", "min-height": "500px"}):
				IGMap(
					center=center.value, on_center=center.set,
					zoom=zoom.value, on_zoom=zoom.set,
					controls=controls.value, layers=layers.value,
					height="100%",
				)

		with solara.Card(style={"margin": "0 !important"}):
			with solara.Column(style={"gap": "20px"}):
				with solara.Row(style={"align-items": "center", "justify-content": "space-between", "flex-wrap": "wrap"}):
					solara.Text("Desempenho dos Modelos", style={"font-size": "20px", "font-weight": "bold"})
					solara.Button(
						"Sobre Modelos e Métricas" if not show_info.value else "Fechar",
						icon_name="info" if not show_info.value else "close",
						on_click=lambda: show_info.set(not show_info.value),
						text=True, outlined=True, style={"text-transform": "none", "font-size": "12px"},
					)

				if show_info.value:
					with solara.Card(style={"background": "#f5f5f5"}):
						ModelsInfo()
				else:
					with solara.Row(style={"gap": "10px", "margin": "10px 0"}):
						solara.Button(
							"Gráficos", on_click=lambda: view_mode.set("graficos"),
							color="primary" if view_mode.value == "graficos" else None,
							outlined=view_mode.value != "graficos", style={"text-transform": "none"},
						)
						solara.Button(
							"Tabela", on_click=lambda: view_mode.set("tabela"),
							color="primary" if view_mode.value == "tabela" else None,
							outlined=view_mode.value != "tabela", style={"text-transform": "none"},
						)

					if view_mode.value == "graficos":
						with solara.ColumnsResponsive(12, large=[6, 6], style={}):
							ModelPerformanceByMetric(models_config=BS_COFFEE_YIELD_CLASSES)
							ModelPerformanceByModel(models_config=BS_COFFEE_YIELD_CLASSES)
					else:
						ModelPerformanceTable(models_config=BS_COFFEE_YIELD_CLASSES)

	return DataLoadingWrapper(
		is_loading=is_loading.value,
		error_message=error_message.value,
		data_ready=data_ready.value,
		on_retry=on_load,
		children=[main],
	)