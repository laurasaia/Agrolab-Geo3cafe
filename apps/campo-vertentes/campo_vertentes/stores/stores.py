"""
Store global para estados compartilhados da aplicação.
Centraliza dados e estados que precisam ser acessados por múltiplos componentes.

Stores disponíveis:
- GeoDataStore: Gerencia dados dos municípios (Campo Vertentes)
- CoffeeGeoDataStore: Gerencia dados de café (IG Café)
- LayersStore: Gerencia camadas WMS do mapa
- EELayersStore: Gerencia camadas Earth Engine do mapa
"""

import urllib.parse
from typing import Dict, Optional

import geopandas as gpd
import solara
from ipyleaflet import TileLayer, VectorTileLayer, WMSLayer


class GeoDataStore:
	"""
	Store para gerenciar o GeoDataFrame dos municípios (Campo Vertentes).
	Estado global carregado na inicialização.
	"""

	def __init__(self):
		# Estados reativos
		self._gdf = solara.reactive(gpd.GeoDataFrame())
		self._center = solara.reactive((-21.0, -44.0))  # Centro aproximado de MG
		self._bounds = solara.reactive(None)
		self._geojson = solara.reactive({"type": "FeatureCollection", "features": []})
		self._loading = solara.reactive(False)
		self._error = solara.reactive(None)
		self._load_attempted = (
			False  # Flag para evitar múltiplas tentativas de carregamento
		)

	@property
	def gdf(self):
		"""GeoDataFrame dos municípios (read-only)."""
		return self._gdf.value

	@property
	def center(self):
		"""Centro do mapa (read-only)."""
		return self._center.value

	@property
	def bounds(self):
		"""Bounds do mapa (read-only)."""
		return self._bounds.value

	@property
	def geojson(self):
		"""GeoJSON dos municípios (read-only)."""
		return self._geojson.value

	@property
	def loading(self):
		"""Estado de carregamento (read-only)."""
		return self._loading.value

	@property
	def error(self):
		"""Mensagem de erro (read-only)."""
		return self._error.value

	def is_loaded(self) -> bool:
		"""Verifica se os dados já foram carregados."""
		return not self._gdf.value.empty

	def ensure_loaded(self, mode="wfs"):
		"""Garante que os dados estão carregados. Se não estiverem, carrega."""
		# Se já está carregando, não tentar novamente
		if self._loading.value:
			return

		# Se não está carregado e ainda não tentou, ou se houve erro, tentar carregar
		if not self.is_loaded() and (not self._load_attempted or self._error.value):
			self._load_attempted = True
			self.load_districts_gdf(mode=mode)

	def load_districts_gdf(self, mode="wfs"):
		"""
		Carrega o GeoDataFrame dos municípios via WFS (GeoServer).

		Args:
		        mode (str): Modo de carregamento dos dados.
		        - "wfs": carregar via WFS (Web Feature Service)
		"""
		from ..config import WFS_MUNICIPIOS, WFS_URL, WFS_VERSION

		self._loading.set(True)
		self._error.set(None)

		try:
			if mode == "shp":
				raise ValueError(
					"Modo 'shp' desativado. Este projeto usa somente GeoServer via mode='wfs'."
				)
			elif mode == "wfs":
				params = {
					"service": "WFS",
					"version": WFS_VERSION,
					"request": "GetFeature",
					"typeName": WFS_MUNICIPIOS,
					"outputFormat": "application/json",
				}

				url = WFS_URL + "?" + "&".join([f"{k}={v}" for k, v in params.items()])
				print("Carregando dados WFS de:", url)
				gdf = gpd.read_file(url)
			else:
				raise ValueError(f"Modo inválido: {mode}")

			# Processar dados
			if "geocodigo" in gdf.columns:
				gdf.set_index("geocodigo", inplace=True)

			# Atualizar estados reativos
			self._gdf.set(gdf)

			gdf_bounds = gdf.total_bounds
			self._center.set(
				(
					float((gdf_bounds[1] + gdf_bounds[3]) / 2),
					float((gdf_bounds[0] + gdf_bounds[2]) / 2),
				)
			)
			self._bounds.set(gdf_bounds)
			self._geojson.set(gdf.copy().__geo_interface__)
			self._loading.set(False)

		except Exception as e:
			error_msg = f"Erro ao carregar dados: {e}"
			print(f"⚠️ {error_msg}")
			self._error.set(error_msg)
			# Resetar flag para permitir retry
			self._load_attempted = False
			# Manter GeoDataFrame vazio em vez de initialize_empty_gdf para não quebrar a lógica is_loaded
			self._gdf.set(gpd.GeoDataFrame())
			self._loading.set(False)


class CoffeeGeoDataStore:
	"""
	Store para gerenciar o GeoDataFrame de café (IG Café).
	Dados carregados sob demanda por município.
	"""

	def __init__(self):
		# Estados reativos
		self._gdf = solara.reactive(gpd.GeoDataFrame())
		self._center = solara.reactive((0, 0))
		self._bounds = solara.reactive(None)
		self._geojson = solara.reactive({"type": "FeatureCollection", "features": []})
		self._loading = solara.reactive(False)
		self._error = solara.reactive(None)
		self._vectortile_layer = solara.reactive(None)

		# Cache simples por município
		self._cache = {}

	@property
	def gdf(self):
		"""GeoDataFrame de café (read-only)."""
		return self._gdf.value

	@property
	def center(self):
		"""Centro do mapa (read-only)."""
		return self._center.value

	@property
	def bounds(self):
		"""Bounds do mapa (read-only)."""
		return self._bounds.value

	@property
	def geojson(self):
		"""GeoJSON de café (read-only)."""
		return self._geojson.value

	@property
	def loading(self):
		"""Estado de carregamento (read-only)."""
		return self._loading.value

	@property
	def error(self):
		"""Mensagem de erro (read-only)."""
		return self._error.value

	@property
	def vectortile_layer(self):
		"""Camada de café em formato VectorTile (read-only)."""
		return self._vectortile_layer.value

	def clear_cache(self):
		"""Limpa o cache de dados de café."""
		self._cache = {}

	def load_coffee_as_vectortile(self, cd_mun=None):
		"""Carrega a camada de café como Vector Tiles usando WMTS."""
		from ..config import COFFEE_LAYER, COFFEE_LAYER_COLOR, WMTS_TEMPLATE_URL

		self._loading.set(True)
		self._error.set(None)

		try:
			base_url = WMTS_TEMPLATE_URL.replace("<LAYER_NAME>", COFFEE_LAYER).replace(
				"<TILE_FORMAT>", "application/vnd.mapbox-vector-tile"
			)

			params = {}
			if cd_mun:
				params["CQL_FILTER"] = f"CD_MUN={cd_mun}"

			query_string = urllib.parse.urlencode(params)
			url = f"{base_url}&{query_string}" if query_string else base_url

			layer_name_in_tile = COFFEE_LAYER.split(":")[-1]

			vector_tile_styles = {
				layer_name_in_tile: {
					"color": COFFEE_LAYER_COLOR,
					"weight": 2,
					"fillOpacity": 0,
					"fillColor": COFFEE_LAYER_COLOR,
					"fill": True,
				}
			}

			vt_layer = VectorTileLayer(
				url=url, name="Café", vector_tile_layer_styles=vector_tile_styles
			)
			print(vt_layer)

			self._vectortile_layer.set(vt_layer)
			# Limpar GDF antigo para economizar memória
			self._gdf.set(gpd.GeoDataFrame())
			self._geojson.set({"type": "FeatureCollection", "features": []})
			self._loading.set(False)

		except Exception as e:
			error_msg = f"Erro ao carregar camada de café (vector tile): {e}"
			print(f"⚠️ {error_msg}")
			self._error.set(error_msg)
			self._loading.set(False)

	def load_coffee_gdf(self, mode="wfs", cd_mun=None):
		"""Carrega o GeoDataFrame de café via WFS (GeoServer).

		Args:
		        mode (str): Modo de carregamento dos dados.
		        cd_mun (str, optional): Código do município para filtrar os dados.
		"""
		from ..config import COFFEE_LAYER, WFS_URL, WFS_VERSION

		self._loading.set(True)
		self._error.set(None)

		try:
			if mode == "shp":
				raise ValueError(
					"Modo 'shp' desativado. Este projeto usa somente GeoServer via mode='wfs'."
				)
			elif mode == "wfs":
				params = {
					"service": "WFS",
					"version": WFS_VERSION,
					"request": "GetFeature",
					"typeName": COFFEE_LAYER,
					"outputFormat": "application/json",
					"srsName": "EPSG:4326",
				}

				# Adicionar filtro CQL se município especificado
				if cd_mun is not None:
					params["CQL_FILTER"] = f"CD_MUN='{cd_mun}'"

				url = WFS_URL + "?" + "&".join([f"{k}={v}" for k, v in params.items()])
				gdf = gpd.read_file(url)
			else:
				raise ValueError(f"Modo inválido: {mode}")

			# Definir índice se houver coluna apropriada e dados
			if not gdf.empty:
				if "CD_MUN" in gdf.columns:
					gdf.set_index("CD_MUN", inplace=True)
				elif "geocodigo" in gdf.columns:
					gdf.set_index("geocodigo", inplace=True)

			# Atualizar estados reativos
			self._gdf.set(gdf)

			# Atualizar center e bounds apenas se houver dados
			if not gdf.empty:
				gdf_bounds = gdf.total_bounds
				self._center.set(
					(
						float((gdf_bounds[1] + gdf_bounds[3]) / 2),
						float((gdf_bounds[0] + gdf_bounds[2]) / 2),
					)
				)
				self._bounds.set(gdf_bounds)
				self._geojson.set(gdf.copy().__geo_interface__)
			else:
				self._geojson.set({"type": "FeatureCollection", "features": []})

			self._loading.set(False)

		except Exception as e:
			error_msg = f"Erro ao carregar dados de café: {e}"
			print(f"⚠️ {error_msg}")
			self._error.set(error_msg)
			# Manter GeoDataFrame vazio
			self._gdf.set(gpd.GeoDataFrame())
			self._geojson.set({"type": "FeatureCollection", "features": []})
			self._loading.set(False)


class LayerInfo:
	"""
	Informações sobre uma camada WMS.
	"""

	def __init__(self, name: str, layer_name: str, wms_url: str, wmts_url: str):
		self.name = name
		self.layer_name = layer_name
		self.wms_url = wms_url
		self.wmts_template_url = wmts_url
		self.layer_instance: Optional[WMSLayer] = None
		self.visible = solara.reactive(False)
		self.opacity = solara.reactive(1.0)  # Opacidade padrão

	def get_or_create_layer(self, mode="wms") -> WMSLayer | TileLayer:
		"""Cria a camada WMS se ainda não existir."""
		if self.layer_instance is None:
			if mode == "wms":
				self.layer_instance = WMSLayer(
					url=self.wms_url + "?tiled=true",
					layers=self.layer_name,
					format="image/jpeg",
					transparent=True,
					name=self.name,
					tiled=True,
					opacity=self.opacity.value,
				)
			elif mode == "wmts":
				url = self.wmts_template_url.replace(
					"<LAYER_NAME>", self.layer_name
				).replace("<TILE_FORMAT>", "image/png")

				self.layer_instance = TileLayer(
					name=self.name,
					url=url,
					opacity=self.opacity.value,
					tile_size=256,
				)
		else:
			# Atualizar opacidade se a camada já existe
			self.layer_instance.opacity = self.opacity.value

		return self.layer_instance

	def toggle_visibility(self):
		"""Alterna a visibilidade da camada."""
		self.visible.set(not self.visible.value)

	def set_visibility(self, visible: bool):
		"""Define a visibilidade da camada."""
		self.visible.set(visible)

	def set_opacity(self, opacity: float):
		"""Define a opacidade da camada."""
		self.opacity.set(opacity)
		# Atualizar a instância da camada se ela existir
		if self.layer_instance is not None:
			self.layer_instance.opacity = opacity


class LayersStore:
	"""
	Store para gerenciar camadas do mapa para municípios.
	Mantém um dicionário de camadas que podem ser compartilhadas entre componentes.
	Implementado como Singleton para garantir uma única instância.
	"""

	_instance = None

	def __new__(cls):
		if cls._instance is None:
			cls._instance = super().__new__(cls)
			cls._instance._initialized = False
		return cls._instance

	def __init__(self):
		if self._initialized:
			return

		from ..config import CLASSES, WMS_URL, WMTS_TEMPLATE_URL

		self.wms_url = WMS_URL
		self.wmts_template_url = WMTS_TEMPLATE_URL  # Ajuste se houver URL WMTS separada
		self.layers: Dict[str, LayerInfo] = {}

		# Lista ordenada de camadas visíveis (última habilitada no topo)
		self._visible_order = solara.reactive([])

		# Inicializar camadas a partir de CLASSES
		for class_key, class_info in CLASSES.items():
			if "layer" in class_info:
				self.layers[class_key] = LayerInfo(
					name=str(class_info["label"]),
					layer_name=str(class_info["layer"]),
					wmts_url=self.wmts_template_url,
					wms_url=self.wms_url,
				)

		self._initialized = True

	def get_layer(self, class_key: str) -> Optional[LayerInfo]:
		"""Retorna informações da camada."""
		return self.layers.get(class_key)

	def get_visible_order(self) -> list:
		"""Retorna a lista ordenada de chaves de camadas visíveis."""
		return self._visible_order.value

	def get_visible_layers(self) -> list:
		"""Retorna lista de instâncias de camadas visíveis ordenadas (última habilitada no topo)."""
		visible = []
		# Retornar na ordem inversa (primeira da lista vai para o topo do mapa)
		for class_key in reversed(self._visible_order.value):
			if class_key in self.layers and self.layers[class_key].visible.value:
				visible.append(self.layers[class_key].get_or_create_layer(mode="wmts"))
		return visible

	def toggle_layer(self, class_key: str):
		"""Alterna visibilidade de uma camada."""
		if class_key in self.layers:
			was_visible = self.layers[class_key].visible.value
			self.layers[class_key].toggle_visibility()

			# Atualizar ordem de visibilidade
			current_order = self._visible_order.value.copy()

			if not was_visible:  # Agora está visível
				# Remover se já estava na lista
				if class_key in current_order:
					current_order.remove(class_key)
				# Adicionar no início (topo)
				current_order.insert(0, class_key)
			else:  # Agora está invisível
				# Remover da lista
				if class_key in current_order:
					current_order.remove(class_key)

			self._visible_order.set(current_order)

	def set_layer_opacity(self, class_key: str, opacity: float):
		"""Define a opacidade de uma camada."""
		if class_key in self.layers:
			self.layers[class_key].set_opacity(opacity)

	def set_layer_visibility(self, class_key: str, visible: bool):
		"""Define a visibilidade de uma camada e atualiza ordem."""
		if class_key in self.layers:
			was_visible = self.layers[class_key].visible.value
			self.layers[class_key].set_visibility(visible)

			# Atualizar ordem de visibilidade
			current_order = self._visible_order.value.copy()

			if visible and not was_visible:  # Agora está visível
				# Remover se já estava na lista
				if class_key in current_order:
					current_order.remove(class_key)
				# Adicionar no início (topo)
				current_order.insert(0, class_key)
			elif not visible:  # Agora está invisível
				# Remover da lista
				if class_key in current_order:
					current_order.remove(class_key)

			self._visible_order.set(current_order)

	def hide_all(self):
		"""Oculta todas as camadas."""
		for layer_info in self.layers.values():
			layer_info.set_visibility(False)
		self._visible_order.set([])
