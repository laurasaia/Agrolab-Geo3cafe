import solara


@solara.component
def StatCard(label: str, value: str, color: str = "#e3f2fd", evolution: float = None):
	"""
	Componente de card reutilizável para exibir estatísticas.

	Args:
	    label: Texto descritivo da estatística
	    value: Valor a ser exibido
	    color: Cor de fundo do card
	    evolution: Percentual de evolução (opcional). Valores positivos indicam crescimento, negativos indicam queda.
	"""
	with solara.Card(
		margin=0, style={"background-color": color, "position": "relative", "flex": "1"}
	):
		with solara.Column(
			gap="5px",
			style={
				"background-color": "transparent",
				"justify-content": "center",
				"align-items": "center",
			},
		):
			solara.Text(
				label,
				style={
					"background-color": "transparent",
					"font-size": "14px",
					"color": "#666",
					"text-align": "center",
				},
			)
			solara.Text(
				value,
				style={
					"background-color": "transparent",
					"font-weight": "bold",
					"font-size": "24px",
				},
			)

		# Exibir indicador de evolução se fornecido (posicionamento absoluto)
		if evolution is not None and evolution != 0:
			evolution_color = "#4caf50" if evolution >= 0 else "#f44336"
			evolution_icon = "▲" if evolution >= 0 else "▼"
			evolution_text = f"{evolution_icon} {abs(evolution):.1f}%"

			solara.Text(
				evolution_text,
				style={
					"position": "absolute",
					"top": "0",
					"right": "6px",
					"background-color": "transparent",
					"font-size": "11px",
					"color": evolution_color,
					"font-weight": "600",
				},
			)


@solara.component
def StatCardsRow(gdf, year, variables_dict):
	"""
	Componente que exibe uma linha de cards estatísticos com base nos dados filtrados por ano.

	Args:
	    variables_dict: Dicionário com as variáveis e suas configurações
	    gdf: GeoDataFrame contendo os dados
	    year: Ano selecionado para filtragem dos dados
	"""
	# Filtrar dados da região pelo ano selecionado
	filtered_region = gdf[gdf["ano"] == year]
	filtered_prev_region = gdf[gdf["ano"] == (year - 1)]

	if len(filtered_region) > 0:
		num_municipios = len(filtered_region)

		with solara.Div(
			style={
				"display": "flex",
				"flex-direction": "row",
				"width": "100%",
				"justify-content": "space-between",
				"align-itens": "center",
				"flex-wrap": "wrap",
				"gap": "10px",
			}
		):
			StatCard("Municípios", f"{num_municipios}")
			for key, info in variables_dict.items():
				total_value = filtered_region[key].sum()
				total_value_prev = filtered_prev_region[key].sum()
				evolucao_value = (
					((total_value - total_value_prev) / total_value_prev * 100)
					if total_value_prev > 0
					else 0
				)

				StatCard(
					info["label"],
					f"{total_value:,.0f}".replace(",", "."),
					evolution=evolucao_value,
				)
	else:
		with solara.Card(style={"padding": "15px"}):
			solara.Text("Sem dados disponíveis para este ano.")
