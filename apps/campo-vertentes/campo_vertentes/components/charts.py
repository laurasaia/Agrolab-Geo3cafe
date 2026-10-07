import plotly.graph_objects as go
import solara

from .view_listener.view_listener import ViewListener


def hex_to_rgb(hex_color):
	"""Converte cor hexadecimal para formato RGB string."""
	hex_color = hex_color.lstrip("#")
	r, g, b = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
	return f"rgb({r},{g},{b})"


@solara.component
def RankingChart(
	gdf, yield_filter, year, coffee_yield_vars, on_click, colormap, bg_color="#e0e0e0"
):
	# Ordenar municípios pelo valor da métrica selecionada no ano atual
	if gdf is None:
		return solara.Text("Loading ranking...")
	else:
		filtered_gdf = gdf[gdf["ano"] == year].copy()
		filtered_gdf = filtered_gdf.sort_values(by=yield_filter, ascending=True)

		# Obter cores individuais para cada município baseado na classificação
		# vmin -> [pallete start], vmax -> [palette end]
		palette_rgb = [
			hex_to_rgb(color) for color in coffee_yield_vars[yield_filter]["palette"]
		]

		# Formatar valores customizados para hover
		text = (
			filtered_gdf[yield_filter]
			.apply(lambda x: f"{x:,.0f}".replace(",", "."))
			.tolist()
		)

		view_data = solara.use_reactive({"width": 600, "height": 500})
		width, height = view_data.value["width"], view_data.value["height"]

		# Criar gráfico de barras
		fig = go.Figure(
			data=[
				go.Bar(
					x=filtered_gdf[yield_filter].tolist(),
					y=filtered_gdf["nome"].tolist(),
					orientation="h",
					marker=dict(
						color=filtered_gdf[f"pct_{yield_filter}"].tolist(),
						colorscale=[
							[i / (len(palette_rgb) - 1), palette_rgb[i]]
							for i in range(len(palette_rgb))
						],
						cmin=filtered_gdf[f"pct_{yield_filter}"].min(),
						cmax=filtered_gdf[f"pct_{yield_filter}"].max(),
						line=dict(color="#333", width=0.75),
					),
					text=text,
					textposition="auto",
					textfont=dict(size=10),
					customdata=text,
					hovertemplate="<b>%{y}</b><br>"
					+ coffee_yield_vars[yield_filter]["label"]
					+ ": %{customdata}<extra></extra>",
				)
			],
			layout=go.Layout(
				template="plotly_white",
				autosize=True,
				paper_bgcolor=bg_color,
				plot_bgcolor=bg_color,
				width=width,
				height=height,
				margin=dict(l=15, r=15, t=40, b=40, pad=2),
				xaxis=dict(title=coffee_yield_vars[yield_filter]["label"]),
				yaxis=dict(title="Município", automargin=True),
			),
		)

		with ViewListener(
			view_data=view_data.value,
			on_view_data=view_data.set,
			style={"width": "100%", "height": "500px"},
		):
			solara.FigurePlotly(
				fig,
				on_click=on_click,
			)


@solara.component
def TimeSeriesChart(district_data, variables_dict, bg_color="#e0e0e0"):
	"""
	Componente que exibe um gráfico de linha com série temporal.

	Args:
	    district_data: DataFrame com dados do município
	    variables_dict: Dicionário com as variáveis e suas configurações
	    bg_color: Cor de fundo do gráfico
	"""
	view_data = solara.use_reactive({"width": 800, "height": 500})

	if len(district_data) > 0:
		line_vars = [col for col in variables_dict]

		width, height = view_data.value["width"], view_data.value["height"]

		fig = go.Figure(
			data=[
				go.Scatter(
					x=district_data["ano"],
					y=district_data[var],
					mode="lines+markers",
					name=variables_dict[var]["label"],
					line=dict(color=variables_dict[var]["color"]),
					hovertemplate="<b>%{fullData.name}</b><br>Ano: %{x}<br>Valor: %{y:,.0f}<extra></extra>".replace(
						",", "."
					),
				)
				for var in line_vars
			],
			layout=go.Layout(
				legend_title_text="Legenda",
				template="plotly_white",
				paper_bgcolor=bg_color,
				plot_bgcolor=bg_color,
				width=width,
				height=height,
				autosize=True,
				xaxis=dict(title="Ano"),
				yaxis=dict(title="Valor"),
			),
		)

		# PlotlyViewListener(figure=fig.to_plotly_json(), style={"width": "100%", "height": "500px"})
		with ViewListener(
			view_data=view_data.value,
			on_view_data=view_data.set,
			style={"width": "100%", "height": "500px"},
		):
			solara.FigurePlotly(fig)
	else:
		solara.Text("Sem dados disponíveis para este município.")


@solara.component
def PointTimeSeriesChart(timeseries_data, bg_color="#e0e0e0"):
	"""
	Componente que exibe um gráfico de linha com série temporal dos índices de um ponto.

	Args:
	    timeseries_data: Dados de série temporal do ponto (lista com timestamp e índices)
	    bg_color: Cor de fundo do gráfico
	"""
	view_data = solara.use_reactive({"width": 800, "height": 500})

	if timeseries_data and len(timeseries_data) > 0:
		# Extrair timestamps e valores dos índices
		timestamps = [item["timestamp"] for item in timeseries_data]
		evi_values = [item.get("evi") for item in timeseries_data]
		ndvi_values = [item.get("ndvi") for item in timeseries_data]

		width, height = view_data.value["width"], view_data.value["height"]

		fig = go.Figure(
			data=[
				go.Scatter(
					x=timestamps,
					y=evi_values,
					name="EVI",
					line=dict(color="#2E7D32", width=2),
					marker=dict(size=6),
					hovertemplate="<b>EVI</b><br>Data: %{x}<br>Valor: %{y:.4f}<extra></extra>",
				),
				go.Scatter(
					x=timestamps,
					y=ndvi_values,
					name="NDVI",
					line=dict(color="#1976D2", width=2),
					marker=dict(size=6),
					hovertemplate="<b>NDVI</b><br>Data: %{x}<br>Valor: %{y:.4f}<extra></extra>",
				),
			],
			layout=go.Layout(
				legend_title_text="Índices",
				template="plotly_white",
				paper_bgcolor=bg_color,
				plot_bgcolor=bg_color,
				width=width,
				height=height,
				autosize=True,
				xaxis=dict(
					title="Data",
					tickformat="%d/%m/%Y",
					tickangle=-45,
				),
				yaxis=dict(
					title="Valor do Índice",
					range=[0, 1],
				),
				hovermode="x unified",
			),
		)

		with ViewListener(
			view_data=view_data.value,
			on_view_data=view_data.set,
			style={"width": "100%", "height": "500px"},
		):
			solara.FigurePlotly(fig)
	else:
		with solara.Column(
			style={"align-items": "center", "padding": "40px", "gap": "10px"}
		):
			solara.Text(
				"Habilite o modo de seleção e marque um ponto dentro de uma cafeicultura.",
				style={"font-size": "14px", "color": "#999"},
			)


@solara.component
def ModelPerformanceByMetric(models_config, bg_color="#e0e0e0"):
	"""
	Gráfico de barras que compara todos os modelos em cada métrica.
	Útil para ver qual modelo performa melhor em cada métrica específica.

	Args:
	    models_config: Dicionário com configurações dos modelos (BS_COFFEE_YIELD_CLASSES)
	    bg_color: Cor de fundo do gráfico
	"""

	# Métricas com descrições em PT-BR
	metrics_info = {
		"accuracy": {
			"label": "Acurácia",
			"description": "Proporção de predições corretas em relação ao total de predições",
		},
		"iou": {
			"label": "IoU",
			"description": "Intersection over Union (IoU) quantifica o grau de sobreposição entre duas regiões. "
			"No caso de detecção e segmentação de objetos, o IoU avalia a sobreposição entre a "
			"região Ground Truth e a região Predita.<br><br>"
			"<b>IoU = Área de Interseção / Área de União</b>",
		},
		"dice": {
			"label": "Dice",
			"description": "O coeficiente Dice, também conhecido como F1 score, avalia a similaridade entre as "
			"máscaras preditas e as máscaras ground truth. É calculado como:<br><br>"
			"<b>Dice = (2 × Área de Interseção) / (Área Predita + Área Ground Truth)</b>",
		},
	}

	# Extrair dados dos modelos
	models_data = []
	for model_id, config in models_config.items():
		models_data.append(
			{
				"id": model_id,
				"name": config["label"],
				"color": config["color"],
				"scores": config["scores"],
			}
		)

	view_data = solara.use_reactive({"width": 600, "height": 500})
	width, height = view_data.value["width"], view_data.value["height"]

	fig = go.Figure()

	# Cada modelo será uma trace, com valores para cada métrica no eixo X
	metric_labels = [info["label"] for info in metrics_info.values()]

	for model in models_data:
		values = [model["scores"][metric_key] for metric_key in metrics_info.keys()]

		fig.add_trace(
			go.Bar(
				name=model["name"],
				x=metric_labels,
				y=values,
				text=[f"{v:.1%}" for v in values],
				textposition="outside",
				marker=dict(
					color=model["color"],
					line=dict(color="#333", width=1),
				),
				hovertemplate="<b>%{fullData.name}</b><br>"
				+ "%{x}: %{y:.2%}<br>"
				+ "<extra></extra>",
			)
		)

	fig.update_layout(
		title={
			"text": "Por Métrica",
			"x": 0.5,
			"xanchor": "center",
		},
		template="plotly_white",
		paper_bgcolor=bg_color,
		plot_bgcolor=bg_color,
		width=width,
		height=height,
		autosize=True,
		barmode="group",
		xaxis=dict(title="Métrica"),
		yaxis=dict(
			title="Valor",
			range=[0, 1],
			tickformat=".0%",
		),
		legend=dict(
			orientation="h",
			yanchor="bottom",
			y=1.02,
			xanchor="center",
			x=0.5,
		),
		margin=dict(l=50, r=20, t=100, b=50),
	)

	with ViewListener(
		view_data=view_data.value,
		on_view_data=view_data.set,
		style={"width": "100%", "height": "500px"},
	):
		solara.FigurePlotly(fig)


@solara.component
def ModelPerformanceByModel(models_config, bg_color="#e0e0e0"):
	"""
	Gráfico de barras que compara todas as métricas de cada modelo.
	Útil para ver o perfil de desempenho completo de cada modelo.

	Args:
	    models_config: Dicionário com configurações dos modelos (BS_COFFEE_YIELD_CLASSES)
	    bg_color: Cor de fundo do gráfico
	"""

	# Métricas com descrições em PT-BR
	metrics_info = {
		"accuracy": {
			"label": "Acurácia",
			"description": "Proporção de predições corretas em relação ao total de predições",
		},
		"iou": {
			"label": "IoU",
			"description": "Intersection over Union (IoU) quantifica o grau de sobreposição entre duas regiões. "
			"No caso de detecção e segmentação de objetos, o IoU avalia a sobreposição entre a "
			"região Ground Truth e a região Predita.<br><br>"
			"<b>IoU = Área de Interseção / Área de União</b>",
		},
		"dice": {
			"label": "Dice",
			"description": "O coeficiente Dice, também conhecido como F1 score, avalia a similaridade entre as "
			"máscaras preditas e as máscaras ground truth. É calculado como:<br><br>"
			"<b>Dice = (2 × Área de Interseção) / (Área Predita + Área Ground Truth)</b>",
		},
	}

	# Extrair dados dos modelos
	models_data = []
	for model_id, config in models_config.items():
		models_data.append(
			{
				"id": model_id,
				"name": config["label"],
				"color": config["color"],
				"scores": config["scores"],
			}
		)

	view_data = solara.use_reactive({"width": 600, "height": 500})
	width, height = view_data.value["width"], view_data.value["height"]

	fig = go.Figure()

	metric_colors = {
		"accuracy": "#28399B",
		"iou": "#4275A5",
		"dice": "#5DA6D6",
	}

	for metric_key, metric_info in metrics_info.items():
		values = [model["scores"][metric_key] for model in models_data]
		names = [model["name"] for model in models_data]

		fig.add_trace(
			go.Bar(
				name=metric_info["label"],
				x=names,
				y=values,
				text=[f"{v:.1%}" for v in values],
				textposition="outside",
				marker=dict(
					color=metric_colors[metric_key],
					line=dict(color="#333", width=1),
				),
				customdata=[[metric_info["description"]] for _ in names],
				hovertemplate="<b>%{x}</b><br>"
				+ metric_info["label"]
				+ ": %{y:.2%}<br>"
				+ "<extra></extra>",
			)
		)

	fig.update_layout(
		title={
			"text": "Por Modelo",
			"x": 0.5,
			"xanchor": "center",
		},
		template="plotly_white",
		paper_bgcolor=bg_color,
		plot_bgcolor=bg_color,
		width=width,
		height=height,
		autosize=True,
		barmode="group",
		xaxis=dict(title="Modelo"),
		yaxis=dict(
			title="Valor",
			range=[0, 1],
			tickformat=".0%",
		),
		legend=dict(
			orientation="h",
			yanchor="bottom",
			y=1.02,
			xanchor="center",
			x=0.5,
		),
		margin=dict(l=50, r=20, t=100, b=50),
	)

	with ViewListener(
		view_data=view_data.value,
		on_view_data=view_data.set,
		style={"width": "100%", "height": "500px"},
	):
		solara.FigurePlotly(fig)
