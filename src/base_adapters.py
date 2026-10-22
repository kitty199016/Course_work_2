from abc import abstractmethod, ABC
from typing import Generic, TypeVar
from models.base_models import BaseAeroModel, T_model


class AeroAPI(ABC, Generic[T_model]):
    """Основной клиент для запросов """

    @abstractmethod
    def get_data(self, *args, **kwargs) -> T_model:...
