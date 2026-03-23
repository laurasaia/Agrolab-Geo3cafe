def find_geocode_by_name(gdf, name):
	"""
	Encontra o geocódigo de um município dado seu nome.

	Args:
	    gdf: GeoDataFrame com os dados dos municípios
	    name: Nome do município a ser buscado
	"""
	matched = gdf[gdf["nome"].str.lower() == name.lower()]
	if not matched.empty:
		return matched.index[0]
	return None


def find_name_by_geocode(gdf, geocode):
	"""
	Encontra o nome de um município dado seu geocódigo.

	Args:
	    gdf: GeoDataFrame com os dados dos municípios
	    geocode: Geocódigo do município a ser buscado
	"""
	row = gdf.loc[geocode]
	return row["nome"] if row is not None else "Desconhecido"


def initialize_empty_gdf():
	"""
	Inicializa e retorna um GeoDataFrame vazio com a estrutura correta.
	"""
	import geopandas as gpd

	# Criar um GeoDataFrame vazio com colunas padrão
	empty_gdf = gpd.GeoDataFrame(
		columns=["geocodigo", "nome", "geometry"], geometry="geometry"
	)
	empty_gdf.set_index("geocodigo", inplace=True)
	return empty_gdf
