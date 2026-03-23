"""
Stores package - Centraliza a instanciação de todos os stores da aplicação.

Este módulo garante que há apenas uma instância de cada store em toda a aplicação,
seguindo o princípio de estado global único.

Stores disponíveis:
- geo_data_store: Gerencia dados dos municípios (Campo Vertentes) - carregado na inicialização
- coffee_geo_data_store: Gerencia dados de café (IG Café) - lazy loading
- layers_store: Gerencia camadas WMS do mapa
- ee_layers_store: Gerencia camadas Earth Engine do mapa
"""

from .stores import CoffeeGeoDataStore, GeoDataStore, LayersStore

# Instâncias globais únicas dos stores
geo_data_store = GeoDataStore()
coffee_geo_data_store = CoffeeGeoDataStore()
layers_store = LayersStore()

# Exportar instâncias
__all__ = [
	"geo_data_store",
	"coffee_geo_data_store",
	"layers_store",
]
