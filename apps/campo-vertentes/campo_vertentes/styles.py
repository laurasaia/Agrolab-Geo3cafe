"""
Gerenciamento de estilos CSS da aplicação.
Carrega o arquivo style.css usando solara.Style.
"""

from pathlib import Path

import solara

# Caminho para o arquivo CSS principal
STYLE_FILE = Path(__file__).parent / "assets" / "style.css"


@solara.component
def LoadStyles():
	"""
	Carrega os estilos da aplicação.

	Usa solara.Style para carregar o arquivo CSS externo.
	- Modo desenvolvimento: observa mudanças automaticamente
	- Modo produção: carrega apenas uma vez

	Deve ser chamado uma vez no Layout principal.
	"""
	solara.Style(STYLE_FILE)


def set_css_variable(variable: str, value: str) -> str:
	"""
	Define uma variável CSS dinamicamente.

	Args:
	    variable: Nome da variável CSS (sem --)
	    value: Valor da variável

	Returns:
	    String HTML com o estilo inline

	Exemplo:
	    solara.HTML(unsafe_innerHTML=set_css_variable("map-bg-color", "#f0f0f0"))
	"""
	return f"""
    <style>
        :root {{
            --{variable}: {value};
        }}
    </style>
    """


def set_map_bg_color(color: str = "#e0e0e0") -> str:
	"""
	Define a cor de fundo do mapa usando variável CSS.

	Args:
	    color: Cor em formato hex, rgb ou nome

	Returns:
	    String HTML com o estilo inline
	"""
	return set_css_variable("map-bg-color", color)
