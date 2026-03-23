from typing import Tuple

from ipyleaflet import GeomanDrawControl, WidgetControl
from ipywidgets import ToggleButton


def create_geoman_draw_control_with_button(
	on_toggle,
) -> Tuple[GeomanDrawControl, WidgetControl]:
	"""
	Cria um controle Geoman com botão customizado para marcar pontos no mapa.
	Similar ao BDC Explorer: botão customizado que controla o modo de desenho.

	Args:
	    on_toggle: Callback para quando o botão é pressionado (recebe True/False)

	Returns:
	    Tupla (GeomanDrawControl, WidgetControl do botão customizado)
	"""
	# Criar GeomanDrawControl oculto (sem toolbar visível)
	geoman_control = GeomanDrawControl(
		hide_controls=True,  # Esconder toolbar padrão
		marker={
			"pathOptions": {},
			"continueDrawing": False,
			"tooltips": False,
		},
	)

	# Criar botão customizado para ativar/desativar modo de desenho
	draw_button = ToggleButton(
		value=False,
		tooltip="Clique para ativar o modo de seleção de ponto",
		icon="bar-chart",  # Ícone de gráfico
		button_style="",
		layout={"width": "44px", "height": "44px"},
	)

	def on_button_toggle(change):
		"""Callback quando botão é clicado."""
		is_active = change["new"]

		# Atualizar aparência do botão
		if is_active:
			draw_button.icon = "times"  # Ícone X quando ativo
			draw_button.tooltip = "Modo de seleção ativo - Clique aqui para cancelar"
			# Ativar modo de desenho do Geoman
			geoman_control.current_mode = "draw:Marker"
		else:
			draw_button.icon = "bar-chart"  # Ícone gráfico quando inativo
			draw_button.tooltip = "Clique para ativar o modo de seleção de ponto"
			# Desativar modo de desenho do Geoman
			geoman_control.current_mode = None

		# Chamar callback externo
		on_toggle(is_active)

	draw_button.add_class("toggle-btn")
	draw_button.add_class("icon-btn")  # Classe para aumentar tamanho do ícone
	draw_button.observe(on_button_toggle, "value")

	# Criar WidgetControl para o botão com posição topright
	button_control = WidgetControl(
		widget=draw_button,
		position="topright",
	)

	return geoman_control, button_control


def create_geoman_draw_control() -> GeomanDrawControl:
	"""
	Cria um controle Geoman customizado para marcar pontos no mapa.

	Configuração:
	- Apenas modo marker habilitado
	- Outros modos (circlemarker, polygon, polyline) desabilitados
	- Edição e remoção desabilitadas

	Returns:
	    GeomanDrawControl configurado para marcação de pontos
	"""
	geoman_control = GeomanDrawControl(
		# Desabilitar todos exceto marker
		circlemarker={},
		polygon={},
		polyline={},
		rectangle={},
		circle={},
		# Habilitar apenas marker
		marker={
			"pathOptions": {},
			"continueDrawing": False,
			"tooltips": False,
		},
		# Desabilitar edição e remoção
		edit=False,
		remove=False,
		cut=False,
		rotate=False,
		drag=False,
	)

	return geoman_control


def create_show_graph_control(on_toggle) -> WidgetControl:
	"""
	Função auxiliar para criar controle de botão para marcar ponto no mapa e exibir série temporal.

	Args:
	    on_toggle: Callback para quando o botão é pressionado

	Returns:
	    WidgetControl do botão para adicionar aos controles do mapa
	"""
	show_graph_btn = ToggleButton(
		value=False,
		tooltip="Clique para ativar o modo de seleção de ponto",
		icon="bar-chart",
		button_style="",
		layout={"width": "44px", "height": "44px"},
	)
	show_graph_btn.add_class("show-graph-toggle-btn")
	show_graph_btn.observe(lambda change: on_toggle(change["new"]), "value")

	button_control = WidgetControl(widget=show_graph_btn, position="topright")

	return button_control


def create_map_legend_controls(
	legend_widget, legend_visible, on_toggle_legend
) -> Tuple[WidgetControl, WidgetControl]:
	"""
	Função auxiliar para criar controles de legenda do mapa com botão de toggle.

	Args:
	    legend_widget: Widget HTML da legenda (ipywidgets.VBox ou HTML)
	    legend_visible: Reactive boolean indicando visibilidade da legenda
	    on_toggle_legend: Callback para alternar visibilidade

	Returns:
	    Tupla (legend_control, button_control) para adicionar aos controles do mapa
	"""
	# Criar controle de legenda
	legend_control = WidgetControl(widget=legend_widget, position="bottomright")

	# Criar botão de toggle
	legend_toggle_btn = ToggleButton(
		value=legend_visible.value,
		tooltip="Mostrar/Ocultar Legenda",
		icon="list",
		button_style="",
		layout={"width": "44px", "height": "44px"},
	)

	legend_toggle_btn.add_class("toggle-btn")
	legend_toggle_btn.add_class("legend-toggle-btn")
	legend_toggle_btn.add_class("icon-btn")  # Classe para aumentar tamanho do ícone

	legend_toggle_btn.observe(lambda change: on_toggle_legend(change["new"]), "value")

	button_control = WidgetControl(widget=legend_toggle_btn, position="bottomright")

	return legend_control, button_control
