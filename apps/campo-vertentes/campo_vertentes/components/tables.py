import solara


@solara.component
def ModelPerformanceTable(models_config):
	"""
	Componente que exibe uma tabela comparativa do desempenho dos modelos.

	Args:
	    models_config: Dicionário com configurações dos modelos (BS_COFFEE_YIELD_CLASSES)
	"""

	# Preparar dados para a tabela
	table_data = []
	for model_id, config in models_config.items():
		table_data.append(
			{
				"Modelo": config["label"],
				"Nome Completo": config["name"],
				"Acurácia": f"{config['scores']['accuracy']:.2%}",
				"IoU": f"{config['scores']['iou']:.2%}",
				"Dice": f"{config['scores']['dice']:.2%}",
				"Período": config["timespan"],
				"Bandas": ", ".join(config["bands"]),
			}
		)

	with solara.Card(style={"overflow": "auto"}):
		with solara.Column(style={"gap": "15px"}):
			solara.Text(
				"Tabela Comparativa", style={"font-size": "18px", "font-weight": "600"}
			)

			# Cabeçalho da tabela
			with solara.Row(
				style={
					"font-weight": "600",
					"border-bottom": "2px solid #333",
					"padding": "10px 0",
				}
			):
				solara.Text("Modelo", style={"flex": "1", "min-width": "100px"})
				solara.Text(
					"Acurácia",
					style={"flex": "1", "min-width": "80px", "text-align": "center"},
				)
				solara.Text(
					"IoU",
					style={"flex": "1", "min-width": "80px", "text-align": "center"},
				)
				solara.Text(
					"Dice",
					style={"flex": "1", "min-width": "80px", "text-align": "center"},
				)
				solara.Text("Período", style={"flex": "1", "min-width": "100px"})
				solara.Text("Bandas", style={"flex": "2", "min-width": "150px"})

			# Linhas da tabela
			for row in table_data:
				with solara.Row(
					style={"padding": "10px 0", "border-bottom": "1px solid #ddd"}
				):
					solara.Text(
						row["Modelo"],
						style={"flex": "1", "min-width": "100px", "font-weight": "500"},
					)
					solara.Text(
						row["Acurácia"],
						style={
							"flex": "1",
							"min-width": "80px",
							"text-align": "center",
						},
					)
					solara.Text(
						row["IoU"],
						style={
							"flex": "1",
							"min-width": "80px",
							"text-align": "center",
						},
					)
					solara.Text(
						row["Dice"],
						style={
							"flex": "1",
							"min-width": "80px",
							"text-align": "center",
						},
					)
					solara.Text(
						row["Período"], style={"flex": "1", "min-width": "100px"}
					)
					solara.Text(
						row["Bandas"],
						style={"flex": "2", "min-width": "150px", "font-size": "12px"},
					)
