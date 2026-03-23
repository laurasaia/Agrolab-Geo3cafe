"""
Componente reutilizável para gerenciar estados de carregamento de dados.
Evita repetição de código entre as páginas.
"""

from typing import Callable

import solara
from solara.alias import rv


@solara.component
def DataLoadingWrapper(
	is_loading: bool,
	error_message: str | None,
	data_ready: bool,
	on_retry: Callable,
	loading_text: str = "Carregando Dados",
	loading_details: list[str] | None = None,
	children: list = [],
):
	"""
	Componente wrapper para gerenciar estados de loading, erro e dados prontos.

	Args:
	    is_loading: Se os dados estão sendo carregados
	    error_message: Mensagem de erro (None se não houver erro)
	    data_ready: Se os dados foram carregados com sucesso
	    on_retry: Callback para tentar novamente em caso de erro
	    loading_text: Texto principal exibido durante o loading
	    loading_details: Lista de detalhes sobre o que está sendo carregado
	    children: Conteúdo a ser renderizado quando dados estiverem prontos
	"""

	# Estado de erro
	if error_message:
		with solara.Column(
			style={"align-items": "center", "padding": "40px", "gap": "20px"}
		) as main:
			rv.Icon(children=["error_outline"], size=80, color="error")
			solara.Text(
				"Erro ao Carregar Dados",
				style={"font-size": "24px", "font-weight": "bold", "color": "#d32f2f"},
			)
			with solara.Card(
				style={"max-width": "700px", "padding": "20px", "text-align": "center"}
			):
				solara.Text(
					error_message,
					style={
						"white-space": "pre-wrap",
						"color": "#666",
						"margin-bottom": "20px",
					},
				)
				solara.Button(
					"🔄 Tentar Novamente",
					on_click=on_retry,
					color="primary",
					style={"margin-top": "10px"},
				)
				solara.Markdown(
					"""
                    **Dicas:**

                    - Verifique sua conexão com a internet

                    - Contate o suporte se o problema persistir
                    """,
					style={"margin-top": "20px", "text-align": "left"},
				)
		return main

	# Estado de loading
	if is_loading or not data_ready:
		with solara.Column(
			style={"align-items": "center", "padding": "40px", "gap": "20px"}
		) as main:
			rv.ProgressCircular(indeterminate=True, size=80, color="primary")
			solara.Text(
				loading_text,
				style={"font-size": "24px", "font-weight": "600", "color": "#333"},
			)
			if loading_details:
				with solara.Column(style={"align-items": "center", "gap": "10px"}):
					for detail in loading_details:
						solara.Text(
							f"• {detail}", style={"font-size": "14px", "color": "#666"}
						)
			else:
				solara.Text("Aguarde...", style={"font-size": "14px", "color": "#666"})
		return main

	# Estado de dados prontos - renderizar conteúdo
	if data_ready and children:
		return solara.Column(children=children)

	# Fallback: estado inicial
	with solara.Column(
		align="center", style={"padding": "40px", "gap": "20px"}
	) as main:
		rv.ProgressCircular(indeterminate=True, size=80, color="primary")
		solara.Text(
			"Inicializando...",
			style={"font-size": "24px", "font-weight": "600", "color": "#333"},
		)

	return main
