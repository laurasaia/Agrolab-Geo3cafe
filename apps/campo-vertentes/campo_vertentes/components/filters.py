import solara


@solara.component
def Filters(
	is_playing,
	on_toogle_play,
	is_data_ready,
	year,
	on_year_selected,
	yield_filter,
	on_yield_selected,
	coffee_yield_vars,
	years,
	on_open_info,
):
	with solara.Card(
		style={"margin": "0 !important", "elevation": "2", "border-radius": "8px"}
	):
		with solara.Column(gap=5):
			# Toggle para métrica
			with solara.Row(style={"flex-wrap": "wrap",}, justify="space-between"):
				with solara.Row(style={"flex=wrap": "wrap", "margin-bottom":"10px",}):
					for key, info in coffee_yield_vars.items():
						solara.Button(
							info["label"],
							color="primary" if yield_filter == key else "default",
							on_click=lambda k=key: on_yield_selected(k),
							style={"margin-right": "5px", "margin-bottom": "5px"},
						)

				solara.Button(
					"Sobre a visualização",
					icon_name="info",
					on_click=on_open_info,
					text=True, outlined=True, style={"text-transform": "none", "font-size": "12px"},
				)

			with solara.Row(style={"flex-wrap": "wrap", "margin-bottom": "10px"}):
				# Botão Play/Pause
				play_icon = "mdi-pause" if is_playing else "mdi-play"
				solara.IconButton(
					icon_name=play_icon,
					# color="success" if not is_playing else "warning",
					on_click=on_toogle_play,
					disabled=not is_data_ready,
				)

				# Slider de anos (usando valores dinâmicos)
				if years and len(years) > 0:
					tick_labels = []
					for y in range(int(min(years)), int(max(years)) + 1):
						if y == int(min(years)) or y == int(max(years)) or y % 10 == 0:
							tick_labels.append(str(y))
						else:
							tick_labels.append("")

					solara.SliderInt(
						"",
						value=year,
						on_value=on_year_selected,
						min=int(min(years)),
						max=int(max(years)),
						step=1,
						tick_labels=tick_labels,
					)
				else:
					solara.SliderInt(
						"",
						value=year,
						on_value=on_year_selected,
						min=1988,
						max=2024,
						step=1,
					)
