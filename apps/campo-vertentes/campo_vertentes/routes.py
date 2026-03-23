"""
Routes configuration for the application.
Maps route paths to their display names and optional metadata.
"""

from typing import TypedDict


class RouteConfig(TypedDict):
	"""Configuration for a single route."""

	name: str
	icon: str


# Routes dictionary mapping paths to route configurations
ROUTES: dict[str, RouteConfig] = {
	"/": {"name": "Campo das Vertentes", "icon": "mdi-map-marker-radius"},
	"01_municipios": {"name": "Municípios", "icon": "mdi-city"},
	"02_classificacoes": {"name": "Classificações", "icon": "mdi-map-outline"},
}


def get_route_name(path: str) -> str:
	"""
	Get the display name for a route path.

	Args:
	    path: The route path (e.g., "/" or "municipios")

	Returns:
	    The display name for the route

	Raises:
	    KeyError: If the path is not found in ROUTES
	"""
	return ROUTES[path]["name"]


def get_route_icon(path: str) -> str:
	"""
	Get the icon for a route path.

	Args:
	    path: The route path (e.g., "/" or "municipios")

	Returns:
	    The icon name for the route

	Raises:
	    KeyError: If the path is not found in ROUTES
	"""
	return ROUTES[path]["icon"]


def get_all_routes() -> dict[str, RouteConfig]:
	"""
	Get all available routes.

	Returns:
	    Dictionary mapping paths to route configurations
	"""
	return ROUTES.copy()
