from typing import Any, Dict

import solara

from ..config import CLASSES
from ..stores import layers_store


@solara.component
def LayerControlRow(classe: str, on_toggle_layer=None):
	"""
	Componente para controle de camada com botão de visibilidade e slider de opacidade.

	Args:
	    classe: Chave da classe em CLASSES
	    on_toggle_layer: Callback(str) chamado ao alternar visibilidade da camada
	"""
	# Buscar informações da classe
	classes_dict: Dict[str, Any] = CLASSES
	store = layers_store

	if classe not in classes_dict:
		raise ValueError(
			f"Classe '{classe}' não existe. Opções: {list(classes_dict.keys())}"
		)

	classe_info = classes_dict[classe]
	layer_info = store.get_layer(classe)

	# Observar mudanças na visibilidade
	is_visible = layer_info.visible.value if layer_info else False

	def on_opacity_change(value):
		"""Atualiza a opacidade da camada WMS."""
		if layer_info:
			store.set_layer_opacity(classe, value)

	with solara.Column(
		style={
			"border": "1px solid #ddd",
			"padding": "5px 15px",
			"border-radius": "8px",
			"row-gap": "0",
		}
	):
		# Container para controles (botão + slider)
		with solara.Row(
			style={"align-items": "center", "margin-left": "8px !important"}
		):
			# Label da camada
			solara.Text(
				str(classe_info.get("label", "")),
				style={"color": "#000", "font-size": "13px", "flex": "1"},
			)
			# Botão de visibilidade
			if layer_info:
				solara.IconButton(
					icon_name="mdi-eye" if is_visible else "mdi-eye-off",
					on_click=lambda: on_toggle_layer(classe),
					style={"color": "#007bff" if is_visible else "#6c757d"},
				)

		# Slider de opacidade (apenas para camadas WMS)
		if layer_info:
			opacity_value = (
				layer_info.opacity.value if hasattr(layer_info, "opacity") else 1.0
			)
			with solara.Row(style={"min-width": "120px", "align-items": "center"}):
				solara.SliderFloat(
					label="",
					value=opacity_value,
					on_value=on_opacity_change,
					min=0.0,
					max=1.0,
					step=0.1,
				)


@solara.component
def LegendaRow(classe: str):
	"""
	Gera um widget (VBox) contendo a legenda da classe passada com campo expansível.

	Args:
	    classe: Chave da classe em CLASSES

	Ex:
	    display(gera_legenda_widget("declividade"))
	"""
	expanded = solara.use_reactive(False)

	# Buscar informações da classe
	classes_dict: Dict[str, Any] = CLASSES
	store = layers_store

	if classe not in classes_dict:
		raise ValueError(
			f"Classe '{classe}' não existe. Opções: {list(classes_dict.keys())}"
		)

	classe_info = classes_dict[classe]
	layer_info = store.get_layer(classe)

	# Observar mudanças na visibilidade
	is_visible = layer_info.visible.value if layer_info else False

	def toggle_layer():
		store.toggle_layer(classe)
		expanded.value = not expanded.value  # Expandir legenda ao ativar camada

	with solara.Column(
		style={
			"position": "relative",
			"border": "1px solid #ddd",
			"padding": "5px",
			"border-radius": "4px",
		}
	):
		with solara.Row(
			style={"justify-content": "space-between", "align-items": "center"}
		):
			label = str(classe_info.get("label", ""))

			solara.Text(label, style={"color": "#000", "font-size": "13px"})

			if layer_info:
				solara.IconButton(
					icon_name="mdi-eye" if is_visible else "mdi-eye-off",
					on_click=toggle_layer,
					style={"color": "#007bff" if is_visible else "#6c757d"},
				)

		# Legendas estão em "viz" para WMS e "legend" para EE
		legend_items = classe_info.get("legend", classe_info.get("viz", []))

		with solara.Details(
			summary="Ver legenda",
			expand=False,
		):
			with solara.Column(style={}):
				for item in legend_items:
					color = item["color"]
					label = item["label"]

					solara.Row(
						children=[
							solara.Div(
								style={
									"width": "20px",
									"height": "20px",
									"background-color": color,
									"border": "1px solid black",
								}
							),
							solara.Text(
								label, style={"color": "#000", "font-size": "12px"}
							),
						],
						style={"background-color": "#fff", "gap": "5px"},
					)


@solara.component
def Legenda(on_toggle_layer=None):
	"""Componente de legenda para camadas WMS."""
	with solara.Column(style={"gap": "10px"}):
		# Camadas de Visualização WMS
		solara.Text(
			"Camadas Base",
			style={
				"font-weight": "bold",
				"color": "#333",
				"margin-top": "10px",
				"font-size": "14px",
			},
		)

		# Camadas WMS - usando LayerControlRow
		for classe in CLASSES.keys():
			LayerControlRow(classe, on_toggle_layer=on_toggle_layer)
