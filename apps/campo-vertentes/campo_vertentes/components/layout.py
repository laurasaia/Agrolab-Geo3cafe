import solara

from campo_vertentes.components.footer import Footer
from campo_vertentes.components.header import Header
from campo_vertentes.styles import LoadStyles


@solara.component
def Layout(children=[]):
	"""
	Layout component that wraps all pages with a header and footer.
	Carrega os estilos CSS da aplicação.
	"""
	# Carregar estilos CSS globais
	LoadStyles()

	with solara.Column(
		style={
			"min-height": "100vh",
			"display": "flex",
			"flex-direction": "column",
		}
	) as main:
		# Header with navigation
		Header()

		# Main content area
		solara.Column(style={"padding": "0 20px", "flex-grow": "1"}, children=children)

		# Footer
		Footer()

	return main
