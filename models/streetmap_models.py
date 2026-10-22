from pydantic import model_validator
from typing import Any
from models.base_models import BaseAeroModel

class OpenStreetDataCoordinates(BaseAeroModel):
    """Класс для хранения данных из Open Stree Map"""
    lamin: float
    lamax: float
    lomin: float
    lomax: float

    @model_validator(mode='before')
    @classmethod
    def convert_list_to_dict(cls, data: Any) -> Any:
        # Если на вход пришел список или кортеж, превращаем его в словарь по ключам полей
        if isinstance(data, (list, tuple)):
            # Получаем имена полей модели в правильном порядке ('a', 'b', 'c', 'd')
            fields = list(cls.model_fields.keys())

            # Проверяем, совпадает ли длина списка с количеством полей
            if len(data) != len(fields):
                raise ValueError(f"Список должен содержать ровно {len(fields)} элементов, получено {len(data)}")

            return dict(zip(fields, data))

        return data
