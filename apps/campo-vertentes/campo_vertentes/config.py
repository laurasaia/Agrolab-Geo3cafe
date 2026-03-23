import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# UI Colors
COMPONENTS_BG = "#e0e0e0"
COFFEE_LAYER_COLOR = "#000000"

# === API Configuration ===
API_BASE_URL = os.getenv("API_BASE_URL")
COFFEE_YIELD_JSON = f"{API_BASE_URL}/coffee/yield/"
POINT_TIMESERIES_JSON = f"{API_BASE_URL}/coffee/point"

# === Geoserver Configuration ===
GEOSERVER_URL = os.getenv("GEOSERVER_URL")
GEOSERVER_WORKSPACE = os.getenv("GEOSERVER_WORKSPACE")

# Server WMTS and WMS
WMTS_TEMPLATE_URL = os.getenv("WMTS_TEMPLATE_URL")
WMS_URL = f"{GEOSERVER_URL}/wms"

# Server WFS
WFS_URL = f"{GEOSERVER_URL}/ows"
WFS_VERSION = os.getenv("WFS_VERSION")
WFS_MUNICIPIOS = f"{GEOSERVER_WORKSPACE}:campo_Vertentes"

# Coffee yield truth map
COFFEE_LAYER = f"{GEOSERVER_WORKSPACE}:ig_cafe"

# Carregamento geoespacial é feito exclusivamente via GeoServer (WFS/WMTS)

# Coffee Yield Variables
COFFEE_YIELD_VARS = {
	"area_plantada_ha": {
		"label": "Área Plantada (ha)",
		"color": "#005F00",
		"palette": ["#66AC66", "#54B654", "#2EB82E", "#00AC00", "#008500", "#005F00"],
	},
	"area_colhida_ha": {
		"label": "Área Colhida (ha)",
		"color": "#ff8400",
		"palette": ["#ffc281", "#ffb668", "#ffa544", "#ff9e36", "#fd911f", "#ff8400"],
	},
	"quantidade_produzida_t": {
		"label": "Quantidade Produzida (t)",
		"color": "#8e5500",
		"palette": ["#f5d6b3", "#e6ad66", "#d68f33", "#b46c00", "#a16000", "#8e5500"],
	},
	"rendimento_medio_kg_ha": {
		"label": "Rendimento Médio (kg/ha)",
		"color": "#0300cc",
		"palette": ["#77adf8", "#649aff", "#4096ff", "#2d20ff", "#0400ff", "#0300cc"],
	},
}

# Classification Configurations
CLASSES = {
	"altitude": {
		"label": "Altitude",
		"layer": f"{GEOSERVER_WORKSPACE}:altitude",
		"viz": [
			{"label": "750 – 850 m", "min": 750, "max": 850, "color": "#336600"},
			{"label": "850 – 950 m", "min": 850, "max": 950, "color": "#cde787"},
			{"label": "950 – 1050 m", "min": 950, "max": 1050, "color": "#f8d77b"},
			{"label": "1050 – 1150 m", "min": 1050, "max": 1150, "color": "#c27523"},
			{"label": "1150 – 1250 m", "min": 1150, "max": 1250, "color": "#714e2b"},
			{"label": "1250 – 1350 m", "min": 1250, "max": 1350, "color": "#d7d7d7"},
		],
	},
	"declividade": {
		"label": "Declividade",
		"layer": f"{GEOSERVER_WORKSPACE}:declividade",
		"viz": [
			{"label": "0 - 3% (Plano)", "min": 0, "max": 3, "color": "#fde4d9"},
			{
				"label": "3 - 8% (Suave-ondulado)",
				"min": 3,
				"max": 8,
				"color": "#fdcab5",
			},
			{"label": "8 - 20% (Ondulado)", "min": 8, "max": 20, "color": "#fc8f6f"},
			{
				"label": "20 - 45% (Forte-ondulado)",
				"min": 20,
				"max": 45,
				"color": "#fc6b41",
			},
			{
				"label": "45 - 75% (Montanhoso)",
				"min": 45,
				"max": 75,
				"color": "#f43e27",
			},
			{
				"label": "> 75% (Forte-Montanhoso)",
				"min": 75,
				"max": 126,
				"color": "#bc2322",
			},
		],
	},
	"orientacao-vertentes": {
		"label": "Orientação das Vertentes",
		"layer": f"{GEOSERVER_WORKSPACE}:orientacao-vertentes",
		"viz": [
			{"label": "0 - 45° (N)", "min": 0, "max": 45, "color": "#ff0000"},
			{"label": "45 - 90° (NE)", "min": 45, "max": 90, "color": "#ff7b00"},
			{"label": "90 - 135° (E)", "min": 90, "max": 135, "color": "#ffff00"},
			{"label": "135 - 180° (SE)", "min": 135, "max": 180, "color": "#00c900"},
			{"label": "180 - 225° (S)", "min": 180, "max": 225, "color": "#3fe0ff"},
			{"label": "225 - 270° (SW)", "min": 225, "max": 270, "color": "#007bd0"},
			{"label": "270 - 315° (W)", "min": 270, "max": 315, "color": "#1013c3"},
			{"label": "315 - 360° (NW)", "min": 315, "max": 360, "color": "#fa4fff"},
		],
	},
	"ig-mapa-solo": {
		"label": "Mapa de Solo",
		"layer": f"{GEOSERVER_WORKSPACE}:ig-mapa-solo",
		"viz": [
			{"label": "Afloramento rochoso", "color": "#646464"},
			{"label": "Argissolo vermelho distrófico", "color": "#f07f7f"},
			{"label": "Argissolo vermelho-amarelo distrófico", "color": "#f7c2ff"},
			{"label": "Argissolo vermelho-amarelo eutrófico", "color": "#f7c2ff"},
			{"label": "Cambissolo háplico Tb distrófico", "color": "#d7c5a5"},
			{"label": "Cambissolo háplico Tb eutrófico", "color": "#d7c5a5"},
			{"label": "Corpos dágua", "color": "#a8d6ff"},
			{"label": "Latossolo vermelho distrófico", "color": "#f4b980"},
			{"label": "Latossolo vermelho-amarelo distrófico", "color": "#f7d1a6"},
			{"label": "Neossolo litólico distrófico", "color": "#96b395"},
			{"label": "Nitossolo háplico distrófico", "color": "#734c00"},
		],
	},
	"ndvi": {
		"label": "NDVI",
		"layer": f"{GEOSERVER_WORKSPACE}:BDC_NDVI",
		"viz": [
			{"label": "≤ 0,2", "min": -1.0, "max": 0.2, "color": "#d7191c"},
			{"label": "0,2 – 0,4", "min": 0.2, "max": 0.4, "color": "#fdae61"},
			{"label": "0,4 – 0,6", "min": 0.4, "max": 0.6, "color": "#ffffc0"},
			{"label": "0,6 – 0,8", "min": 0.6, "max": 0.8, "color": "#a6d96a"},
			{"label": "> 0,8", "min": 0.8, "max": 1.0, "color": "#1a9641"},
		],
	},
	"lst": {
		"label": "Temperatura de Superfície (°C)",
		"layer": f"{GEOSERVER_WORKSPACE}:BDC_LST",
		"viz": [
			{"label": "≤ 18 °C", "min": -50, "max": 18, "color": "#19b5f1"},
			{"label": "18 – 23 °C", "min": 18, "max": 23, "color": "#23db3f"},
			{"label": "23 – 27 °C", "min": 23, "max": 27, "color": "#f3f01d"},
			{"label": "27 – 32 °C", "min": 27, "max": 32, "color": "#f57215"},
			{"label": "> 32 °C", "min": 32, "max": 60, "color": "#a4262c"},
		],
	},
}

# Bom Sucesso coffee Yield Prediction Configurations
BS_COFFEE_YIELD_CLASSES = {
	"xgb": {
		"label": "XGBoost",
		"name": "Extreme Gradient Boosting (XGBoost)",
		"color": "#ff6600",
		"timespan": "2019-2022",
		"scores": {
			"accuracy": 0.91,
			"iou": 0.59,
			"dice": 0.74,
		},
		"bands": ["R", "G", "B"],
		"description": "Utiliza árvores de decisão com reforço de gradiente, é conhecido por sua "
		"velocidade, eficiência e habilidade em lidar com grandes volumes de dados."
		"(XGBoost), abrangendo os anos de 2019 a 2022.",
		"wfs_layer": f"{GEOSERVER_WORKSPACE}:bomsucesso_cafe_2019_2022_xgb",
	},
	"ltae": {
		"label": "LightTAE",
		"name": "Lightweight Temporal Attention Encoder (LTAE)",
		"color": "#0099cc",
		"timespan": "2021-2022",
		"scores": {
			"accuracy": 0.87,
			"iou": 0.65,
			"dice": 0.79,
		},
		"bands": ["R", "G", "B", "EVI", "NDVI"],
		"description": "Uma arquitetura de rede neural, frequentemente baseada nos princípios do "
		"Transformer, projetada para processar dados sequenciais, como séries temporais de imagens "
		"de satélite."
		"Attention Encoder (LightTAE), abrangendo os anos de 2021 a 2022.",
		"wfs_layer": f"{GEOSERVER_WORKSPACE}:bomsucesso_cafe_2021_2022_ltae",
	},
	"rf": {
		"label": "Random Forest",
		"name": "Random Forest (RF)",
		"color": "#ffff00",
		"timespan": "2021-2022",
		"scores": {
			"accuracy": 0.88,
			"iou": 0.51,
			"dice": 0.68,
		},
		"bands": ["R", "G", "B", "NIR"],
		"description": "Combina a saída de múltiplas árvores de decisão para alcançar um único "
		"resultado de previsão, ",
		"wfs_layer": f"{GEOSERVER_WORKSPACE}:bomsucesso_cafe_2021_2022_rf",
	},
	"tempcnn": {
		"label": "TempCNN",
		"name": "Temporal Convolutional Neural Network (TempCNN)",
		"color": "#3300ff",
		"timespan": "2021-2022",
		"scores": {
			"accuracy": 0.89,
			"iou": 0.49,
			"dice": 0.66,
		},
		"bands": ["R", "G", "B"],
		"description": "é uma arquitetura de aprendizado profundo projetada especificamente para tarefas "
		" de modelagem de sequências, como previsão de séries temporais e processamento de áudio.",
		"wfs_layer": f"{GEOSERVER_WORKSPACE}:bomsucesso_cafe_2021_2022_tempcnn",
	},
}
