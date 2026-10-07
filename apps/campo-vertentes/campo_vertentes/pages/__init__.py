import asyncio
from typing import Dict

import ipyleaflet as leaflet
import numpy as np
import pandas as pd
import solara
from branca.colormap import LinearColormap
from ipywidgets import HTML, VBox
from solara import use_effect, use_fetch, use_json_load
from solara.alias import rv
from solara.lab import Task, use_task

# Importar Layout para aplicá-lo
from ..components import (
	DataLoadingWrapper,
	Filters,
	IGMap,
	Layout,  # noqa Importação necessária,
	RankingChart,
	StatCardsRow,
	TimeSeriesChart,
	create_map_legend_controls,
)
from ..config import COFFEE_YIELD_JSON, COFFEE_YIELD_VARS, COMPONENTS_BG
from ..stores import geo_data_store
from ..utils import find_geocode_by_name

INITIAL_CONTROLS = [
	leaflet.ZoomControl.element(position="topleft"),
	leaflet.ScaleControl.element(position="bottomleft"),
]


def gerar_classes_porcentagem(df, coluna, n_classes=6):
	"""
	Gera classes baseadas em porcentagem do total.
	Cada município terá um percentual calculado e será classificado.
	"""
	# Calcular o total para cada ano
	print(df.shape, df.columns.tolist())
	total_por_ano = df.groupby("ano")[coluna].transform("sum")

	# Calcular percentual de cada município em relação ao total do ano
	df[f"pct_{coluna}"] = (df[coluna] / total_por_ano) * 100

	# Gerar classes baseadas nos percentuais
	v_min = df[f"pct_{coluna}"].min()
	v_max = df[f"pct_{coluna}"].max()

	# Gera limites igualmente espaçados
	bins = np.linspace(v_min, v_max, n_classes + 1)

	# Formata rótulos com percentuais
	labels = [f"{bins[i]:.1f}% - {bins[i + 1]:.1f}%" for i in range(n_classes)]

	df[f"class_{coluna}"] = pd.cut(
		df[f"pct_{coluna}"], bins=bins, labels=labels, include_lowest=True
	)

	return df, labels

@solara.component
def SobreInfo(on_close):
	about_info = {
		"Exibição ao longo do tempo": {
			"desc": "Aperte o botão de play (▶) para ver os dados avançarem ano a ano, de forma automática. A cada passo, os valores dos cartões, as cores do mapa e as barras do gráfico se atualizam sozinhos, e assim você acompanha a evolução cronológica. Aperte novamente o botão (⏸) para pausar no ano que quiser. Também é possível escolher o ano arrastando a barra cronológica.",
			"color": "#2196F3",
		},
		"Variação dos cartões": {
			"desc": "O número pequeno no canto de cada cartão compara o valor do ano exibido com o do ano anterior, em porcentagem. Verde (▲) significa que o valor aumentou, e vermelho (▼) significa que diminuiu. Por exemplo, ▲ 2,6% indica que o valor está 2,6% maior que no ano anterior.",
			"color": "#2196F3",
		},
	}

	with solara.Card(style={"margin": "0 !important", "border-radius": "8px", "background": "#f5f5f5"}):
		with solara.Row(justify="space-between", style={"align-items": "center", "background": "#f5f5f5"}):
			solara.Text("Sobre a visualização", style={"font-size": "16px", "font-weight": "600"})
			solara.Button(
				"Fechar",
				icon_name="close",
				on_click=on_close,
				text=True, outlined=True,
				style={"text-transform": "none", "font-size": "12px", "background-color": "#FFFFFF"},
			)

		with solara.Div(
			style={
				"display": "grid",
				"grid-template-columns": "repeat(auto-fit, minmax(320px, 1fr))",
				"gap": "10px",
			}
		):
			for title, info in about_info.items():
				with solara.Card(style={"margin": "0", "padding": "0px", "border-left": f"3px solid {info['color']}", "background": "white"}):
					solara.Text(f"{title}: ", style={"font-weight": "600", "font-size": "13px", "margin-bottom": "5px"})
					solara.Text(info["desc"], style={"font-size": "12px", "color": "#666", "line-height": "1.4"})
@solara.component
def Page():
	merged_gdf = solara.use_reactive(None)
	years = solara.use_reactive([])
	layers = solara.use_reactive([])
	geo_layer = solara.use_reactive(None)
	labels_layer = solara.use_reactive(None)
	popup_layer = solara.use_reactive(None)
	legend_content = solara.use_reactive(None)
	legend_visible = solara.use_reactive(False)
	legend_button = solara.use_reactive(None)
	controls = solara.use_reactive(INITIAL_CONTROLS)
	zoom = solara.use_reactive(9)
	center = solara.use_reactive((-21.0, -44.0))  # Centro padrão de MG
	year = solara.use_reactive(2024)
	selected_district = solara.use_reactive(None)
	yield_filter = solara.use_reactive(list(COFFEE_YIELD_VARS.keys())[0])
	yield_colormap = solara.use_reactive(None)

	# Estados para animação
	is_playing = solara.use_reactive(False)
	preprocessed_data = solara.use_reactive({})  # Cache de dados processados por ano
	is_data_ready = solara.use_reactive(False)

	# Estados unificados de loading e erro
	is_loading = solara.use_reactive(False)
	error_message = solara.use_reactive(None)
	data_ready = solara.use_reactive(False)
	show_header = solara.use_reactive(0)
	show_info = solara.use_reactive(False)

	def open_info():
		is_playing.set(False)
		show_info.set(True)
		
	def PageHeader():
		with rv.ExpansionPanels(v_model=show_header.value, on_v_model=show_header.set, style={}):
			with rv.ExpansionPanel():
				with rv.ExpansionPanelHeader():
					with solara.Row(justify="space-between", style={"align-items": "center","margin-right": "8px"}):
						solara.Text("Campo das Vertentes e Cafeicultura", style={"font-size": "18px", "font-weight": "bold"})
						#solara.Text("Ano: 1988-2024", style={"font-size": "16px", "color": "#666"})
				with rv.ExpansionPanelContent():
					with solara.Column(style={"gap": "15px",}):
						solara.Markdown(
							"""
							Este painel apresenta área plantada, área colhida, quantidade produzida e rendimento médio do café
							nos municípios da Indicação Geográfica Campo das Vertentes. Para visualizar os dados de um município específico, selecione-o
							clicando diretamente no mapa. Assim, o gráfico de série temporal abaixo também será atualizado automaticamente com base na sua escolha. Fonte de dados: <a href = "https://sidra.ibge.gov.br/home/pimpfbr/brasil" target="_blank">IBGE/SIDRA</a> (1988-2024), <a href="https://data.inpe.br/bdc/en/home-page-2/" target="_blank">BDC</a> (2017-2026).
							""",
							style={"color": "#495057", "font-size": "14px", "line-height": "1.6"},
						)


	def preprocess_all_years(merged_df: pd.DataFrame) -> Dict[int, pd.DataFrame]:
		"""
		Pré-processa os dados de todos os anos para animação suave.
		Retorna um dicionário com ano como chave e GeoDataFrame filtrado como valor.
		"""
		processed = {}
		sorted_years = sorted(merged_df["ano"].unique())
		years.set(sorted_years)

		for yr in sorted_years:
			filtered = merged_df[merged_df["ano"] == yr].copy()
			if len(filtered) > 0:
				filtered["valor"] = filtered[yield_filter.value]
				processed[yr] = filtered

		return processed

	# Buscar dados da API
	data = use_fetch(COFFEE_YIELD_JSON)
	json = use_json_load(data)

	# Função para retry
	def retry_load():
		error_message.set(None)
		is_loading.set(True)
		data.retry()
		load_essential_data()

	# Efeito único para carregar todos os dados essenciais
	def load_essential_data():
		"""Carrega dados essenciais: municípios (GeoServer) e café (API)."""
		is_loading.set(True)
		error_message.set(None)

		# 1. Carregar dados de municípios via WFS
		geo_data_store.ensure_loaded(mode="wfs")

		# 2. Verificar se houve erro ao carregar municípios
		if geo_data_store.error:
			error_message.set(
				f"Erro ao carregar dados dos municípios: {geo_data_store.error}"
			)
			is_loading.set(False)
			data_ready.set(False)
			return

		# 3. Aguardar carregamento dos municípios
		if geo_data_store.loading:
			return

		# 4. Verificar se municípios foram carregados com sucesso
		if not geo_data_store.is_loaded():
			return

		# 5. Verificar erros da API
		if data.error:
			error_message.set(
				f"Erro ao conectar com a API de dados de café: {str(data.error)}"
			)
			is_loading.set(False)
			data_ready.set(False)
			return

		if json.error:
			error_message.set(f"Erro ao processar dados da API: {str(json.error)}")
			print(data)
			is_loading.set(False)
			data_ready.set(False)
			return

		# 6. Aguardar dados da API
		if not json.value:
			return

		# 7. Todos os dados essenciais carregados com sucesso
		print("✅ Dados essenciais carregados com sucesso")
		center.value = geo_data_store.center
		is_loading.set(False)
		data_ready.set(True)

	use_effect(
		load_essential_data,
		[geo_data_store.loading, data.error, json.error, json.value],
	)

	# Efeito para processar dados da API quando estão prontos
	def process_api_data():
		# Só processar se dados essenciais estão prontos
		if not data_ready.value or not json.value:
			return

		# Extrair dados da API
		api_data = json.value.get("data", [])

		# Flatten dos dados
		rows = []
		for item in api_data:
			for prod in item["producao"]:
				data_row = {
					"geocodigo": str(item["geocodigo"]),
					"ano": prod["ano"],
				}

				for col in COFFEE_YIELD_VARS:
					data_row[col] = prod[col]

				rows.append(data_row)
		df = pd.DataFrame(rows)

		# Gerar classes e cores
		for col in COFFEE_YIELD_VARS:
			classified_df, classes = gerar_classes_porcentagem(df, col, n_classes=6)

			# Mapeia cores conforme ordem das classes usando a paleta específica da variável
			var_palette = COFFEE_YIELD_VARS[col]["palette"]
			color_map = dict(zip(classes, var_palette[: len(classes)]))
			df[f"color_{col}"] = classified_df[f"class_{col}"].map(color_map)

		# Merge com gdf
		df.set_index("geocodigo", inplace=True)
		gdf = geo_data_store.gdf
		merged = gdf.join(df, on="geocodigo", how="left", rsuffix="_data")

		merged_gdf.set(merged)

		# Pré-processar todos os anos para animação suave
		processed = preprocess_all_years(merged)
		preprocessed_data.set(processed)

		is_data_ready.set(True)

	use_effect(process_api_data, [data_ready.value])

	# Task para criar/atualizar camada choropleth
	async def update_choropleth_task():
		if merged_gdf.value is None:
			return

		# Limpar popup atual
		if len(layers.value) > 2:
			# Manter geo_layer e labels_layer, remover apenas popup
			layers.value = [
				layer for layer in layers.value if layer != popup_layer.value
			]
			selected_district.set(None)

		# Filtrar pelo ano selecionado
		filtered_gdf = merged_gdf.value[merged_gdf.value["ano"] == year.value].copy()

		# Criar dicionário para o Choropleth
		choro_dict = {}
		for _, row in filtered_gdf.iterrows():
			geocodigo = row.name
			valor = row[f"pct_{yield_filter.value}"]
			choro_dict[geocodigo] = valor

		if len(filtered_gdf) > 0:
			# Adicionar coluna de valor para o colormap baseado na métrica selecionada
			filtered_gdf["valor"] = filtered_gdf[f"pct_{yield_filter.value}"]

			# Criar legenda usando a paleta específica da variável
			var_palette = COFFEE_YIELD_VARS[yield_filter.value]["palette"]
			legend_html = "<div style='background-color: white; padding: 10px; border: 2px solid #bdbdbd;'>"
			legend_html += (
				f"<b>{COFFEE_YIELD_VARS[yield_filter.value]['label']}</b><br>"
			)

			for cls, color in zip(
				filtered_gdf[f"class_{yield_filter.value}"].cat.categories, var_palette
			):
				legend_html += f"<i style='background:{color};width:18px;height:18px;float:left;margin-right:8px;opacity:0.7;'></i>{cls}<br>"

			legend_html += "</div>"

			legend_widget = VBox([HTML(legend_html)])

			# Converter para GeoJSON
			filtered_geojson = filtered_gdf.__geo_interface__

			# Criar camada de labels com os nomes dos municípios (apenas uma vez)
			if labels_layer.value is None:
				label_markers = []
				for idx, row in filtered_gdf.iterrows():
					# Calcular o centróide do polígono
					centroid = row.geometry.centroid
					lat, lon = centroid.y, centroid.x

					# Criar um DivIcon para o label
					label_html = f"""
                    <div style="
                        font-size: 10px;
                        font-weight: bold;
                        color: #333;
                        text-align: center;
                        text-shadow: -1px -1px 0 white, 1px -1px 0 white, -1px 1px 0 white, 1px 1px 0 white;
                        white-space: nowrap;
                        pointer-events: none;
                    ">
                        {row["nome"]}
                    </div>
                    """

					icon = leaflet.DivIcon(
						html=label_html, icon_size=[80, 16], icon_anchor=[40, 8]
					)
					marker = leaflet.Marker(
						location=(lat, lon),
						icon=icon,
						draggable=False,
						interactive=False,
					)
					label_markers.append(marker)

				# Criar LayerGroup com todos os labels
				new_labels_layer = leaflet.LayerGroup(
					layers=label_markers, name="Labels"
				)
				labels_layer.set(new_labels_layer)

			# Função handler para cliques (reutilizada)
			def on_click_handler(event, feature, **kwargs):
				# Coleta informações do município clicado no 'merged_gdf'
				geocodigo = feature["id"]
				ano = year.value

				# Filtrar corretamente: primeiro pelo geocódigo, depois pelo ano
				municipio_data = merged_gdf.value[merged_gdf.value.index == geocodigo]
				properties = municipio_data[municipio_data["ano"] == ano].iloc[0]

				popup_content = f"""
                    <b>Geocódigo: {geocodigo}</b><br>
                    <b>Município: {properties.get("nome", "N/A")}</b><br>
                    <b>Ano: {properties.get("ano", "N/A")}</b><br>
                """

				for key, info in COFFEE_YIELD_VARS.items():
					valor = properties.get(key, "N/A")
					popup_content += f"""
                        <b>{info["label"]}: {valor}</b><br>
                    """

				# Fechar popup antes de atualizar (força re-renderização)
				popup_layer.value.close_popup()

				# Atualizar conteúdo e localização
				popup_layer.value.child = HTML(popup_content)
				popup_layer.value.location = kwargs["coordinates"]

				# Abrir popup com novo conteúdo
				popup_layer.value.open_popup()
				selected_district.set(geocodigo)

				# Adicionar popup às layers no primeiro clique
				if popup_layer.value not in layers.value:
					layers.value = [
						geo_layer.value,
						labels_layer.value,
						popup_layer.value,
					]

			# Atualizar ou criar camada
			# Criar colormap baseado na métrica selecionada
			cm = LinearColormap(
				colors=var_palette,
				vmin=filtered_gdf[f"pct_{yield_filter.value}"].min(),
				vmax=filtered_gdf[f"pct_{yield_filter.value}"].max(),
			)
			yield_colormap.set(cm)

			if geo_layer.value:
				# Atualizar 'data' ou 'choro_data' dependendo da camada existente
				geo_layer.value.choro_data = choro_dict
				geo_layer.value.colormap = cm

				# Atualizar legenda
				if legend_content.value:
					legend_content.value.widget = legend_widget

				# Re-registrar o handler com os dados atualizados
				if popup_layer.value:
					geo_layer.value.on_click(on_click_handler)
			else:
				# Criar popup (não será adicionado às layers até o primeiro clique)
				popup = leaflet.Popup(
					name="Popup",
					close_button=True,
					auto_close=True,
					auto_pan=True,
					close_on_escape_key=True,
				)
				popup_layer.set(popup)

				# Criar nova camada Choropleth
				new_layer = leaflet.Choropleth(
					name="Café",
					geo_data=filtered_geojson,
					choro_data=choro_dict,
					colormap=cm,
					style={"fillOpacity": 0.7, "color": "black", "weight": 1},
					hover_style={"weight": 3, "color": "yellow", "fillOpacity": 0.9},
				)
				new_layer.on_click(on_click_handler)
				geo_layer.value = new_layer

				# Criar legenda usando create_map_legend_controls
				def toggle_legend_handler(is_visible):
					"""Handler para alternar visibilidade da legenda."""
					legend_visible.set(is_visible)
					current_controls = controls.value.copy()
					if is_visible:
						if legend_content.value not in current_controls:
							current_controls.append(legend_content.value)
					else:
						if legend_content.value in current_controls:
							current_controls.remove(legend_content.value)
					controls.value = current_controls

				# Criar controles de legenda
				legend_control, button_control = create_map_legend_controls(
					legend_widget=legend_widget,
					legend_visible=legend_visible,
					on_toggle_legend=toggle_legend_handler,
				)

				legend_content.set(legend_control)

				# Adicionar botão e legenda (se visível) ao mapa
				new_controls = controls.value.copy() + [button_control]
				if legend_visible.value:
					new_controls.append(legend_control)
				controls.value = new_controls

				# Inicialmente adicionar a camada GeoJSON e os labels, sem o popup
				if labels_layer.value:
					layers.value = [geo_layer.value, labels_layer.value]
				else:
					layers.value = [geo_layer.value]

		return

	choro_layer_task: Task = use_task(
		update_choropleth_task,
		dependencies=[year.value, yield_filter.value, merged_gdf.value],
	)

	# Task para controlar a animação
	async def animation_task():
		if not is_data_ready.value or not is_playing.value:
			return

		while is_playing.value:
			# Aguardar que o choropleth atual termine de renderizar
			while is_playing.value and choro_layer_task.pending:
				await asyncio.sleep(0.1)

			# Aguardar intervalo entre frames
			await asyncio.sleep(1.0)

			if not is_playing.value:
				break

			# Usar valores dinâmicos de years
			if years.value and len(years.value) > 0:
				current_index = (
					years.value.index(year.value) if year.value in years.value else 0
				)
				next_index = (current_index + 1) % len(years.value)
				year.set(years.value[next_index])
			else:
				# Fallback para comportamento anterior
				next_year = year.value + 1
				if next_year > 2024:
					year.set(2003)
				else:
					year.set(next_year)

	use_task(animation_task, dependencies=[is_playing.value, is_data_ready.value])

	# Garante que a animação para quando a sessão é encerrada (fechar aba, refresh, etc.)
	def cleanup_on_unmount():
		def cleanup():
			is_playing.set(False)

		return cleanup

	solara.use_effect(cleanup_on_unmount, [])
	with solara.Column(style={"flex-grow": "1", "gap": "15px"}) as main:
		PageHeader()
		with solara.Column():
			if show_info.value:
				SobreInfo(on_close=lambda: show_info.set(False))
			else:
				Filters(
					is_playing=is_playing.value,
					on_toogle_play=lambda: is_playing.set(not is_playing.value),
					is_data_ready=is_data_ready.value,
					year=year.value,
					on_year_selected=year.set,
					yield_filter=yield_filter.value,
					on_yield_selected=lambda key: yield_filter.set(key),
					coffee_yield_vars=COFFEE_YIELD_VARS,
					years=years.value,
					on_open_info=open_info,
				)
				StatCardsRow(merged_gdf.value, year.value, COFFEE_YIELD_VARS)

		# Dados da região em Mapa e Gráfico de Barras
		with solara.Card(margin=0, style={"padding": "0 10px", "position": "relative"}):
			solara.Text(
				f"{COFFEE_YIELD_VARS[yield_filter.value]['label']} - {year.value}",
				style={
					"font-size": "18px",
					"font-weight": "600",
					"position": "absolute",
					"top": "10px",
					"left": "26px",
					"z-index": "1000",
				},
			)
			with solara.ColumnsResponsive(12, large=6, style={"padding-top": "22px"}):
				with solara.Column(
					style={"isolation": "isolate", "position": "relative"}
				):
					if geo_layer.value:
						IGMap(
							center=center.value,
							on_center=center.set,
							zoom=zoom.value,
							on_zoom=zoom.set,
							controls=controls.value,
							layers=layers.value,
							bg_color=COMPONENTS_BG,
						)

						if choro_layer_task.pending:
							with solara.Div(
								style={
									"position": "absolute",
									"top": "0",
									"left": "0",
									"width": "100%",
									"height": "100%",
									"background-color": "transparent",
									"display": "flex",
									"align-items": "center",
									"justify-content": "center",
									"z-index": "500",
								}
							):
								rv.ProgressCircular(
									indeterminate=True, size=64, color="white"
								)
					else:
						with solara.Column(
							style={
								"align-items": "center",
								"padding": "40px",
								"gap": "15px",
							}
						):
							rv.ProgressCircular(
								indeterminate=True, size=64, color="primary"
							)
							solara.Text(
								"Carregando Mapa...",
								style={"font-size": "18px", "color": "#666"},
							)

				with solara.Column():
					RankingChart(
						merged_gdf.value,
						yield_filter=yield_filter.value,
						year=year.value,
						coffee_yield_vars=COFFEE_YIELD_VARS,
						on_click=lambda data: selected_district.set(
							find_geocode_by_name(
								merged_gdf.value, data["points"]["ys"][0]
							)
						),
						colormap=yield_colormap.value,
						bg_color=COMPONENTS_BG,
					)

		# Gráfico de série temporal
		if selected_district.value:
			district_data = merged_gdf.value[
				(merged_gdf.value.index == selected_district.value)
			]
		else:
			district_data = pd.DataFrame()

		# Verificar se há dados antes de renderizar
		if len(district_data) > 0:
			with solara.Card(
				margin=0,
				style={"padding": "0 10px", "position": "relative"},
			):
				solara.Text(
					f"Série Temporal - {district_data.iloc[0]['nome']}",
					style={
						"font-size": "18px",
						"font-weight": "600",
						"position": "absolute",
						"top": "10px",
						"left": "26px",
						"z-index": "1000",
					},
				)
				with solara.Column(style={"padding-top": "22px"}):
					TimeSeriesChart(district_data, COFFEE_YIELD_VARS, COMPONENTS_BG)
		else:
			with solara.Card(margin=0, style={"padding": "20px"}):
				solara.Text(
					"Selecione um município via mapa ou gráfico para visualizar a série temporal.",
					style={"color": "#666"},
				)

	return DataLoadingWrapper(
		is_loading=is_loading.value,
		error_message=error_message.value,
		data_ready=is_data_ready.value,
		on_retry=retry_load,
		children=[main],
	)