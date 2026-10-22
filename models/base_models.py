from pydantic import BaseModel
from typing import TypeVar, Generic

class BaseAeroModel(BaseModel):
    """Базовый класс для моделей данных"""

T_model = TypeVar('T_model', bound=BaseAeroModel, covariant=True)