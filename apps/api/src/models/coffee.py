from typing import Any, List

from pydantic import ConfigDict, Field

from src.models.base_model import CustomBaseModel, OutBaseModel
from bson import ObjectId


class CoffeeYield(CustomBaseModel):
	"""Represents a single coffee yield document from 'producao' collection."""

	id: ObjectId = Field(..., alias="_id")
	geocodigo: str
	municipio: str
	producao: List[dict[str, Any]]

	model_config = ConfigDict(
		arbitrary_types_allowed=True,
	)


class CoffeeYieldOut(OutBaseModel):
	"""Coffee yield output data model."""
	data: List[CoffeeYield]


class PointTimeSeries(CustomBaseModel):
	"""Represents a single point time series document from 'cafe' collection."""

	id: ObjectId = Field(..., alias="_id")
	geocodigo: str
	metadata: dict[str, Any]
	timeseries: List[dict[str, Any]]

	model_config = ConfigDict(
		arbitrary_types_allowed=True,
	)


class PointTimeSeriesFetch(CustomBaseModel):
	"""Point time series input data model."""

	lat: float
	lng: float
	max_distance: int = 10


class PointTimeSeriesOut(OutBaseModel):
	"""Point time series output data model."""
	data: List[PointTimeSeries]

