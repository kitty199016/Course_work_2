import pytest
from unittest.mock import MagicMock
from models.aeroplane_model import AeroplanesDB
from src.aeroplanes_api import AeroplaneAPI


def test_get_data_success(monkeypatch):
    """Тест успешного получения и валидации данных о самолетах через monkeypatch"""

    # 1. Инициализируем наш API класс (пока с реальными клиентами внутри)
    api = AeroplaneAPI()

    # 2. Создаем и настраиваем заглушку для OpenStreetAPI
    mock_coordinates = MagicMock()
    mock_coordinates.model_dump.return_value = {
        "lamin": 36.0, "lamax": 43.8, "lomin": -9.3, "lomax": 3.3
    }
    mock_get_coordinates = MagicMock(return_value=mock_coordinates)

    # Подменяем метод get_data у встроенного объекта coordinates
    monkeypatch.setattr(api.coordinates, "get_data", mock_get_coordinates)

    # 3. Создаем и настраиваем заглушку для метода get нашего APIClient
    mock_api_response = {
        "time": 1618224000,
        "states": [
            ["345123", "IBE3122 ", "Spain", 1618224000, 1618224000, -3.56, 40.47, 10000, False, 230.5, 45, 0, None,
             10050, "3421", False, 0]
        ]
    }
    mock_client_get = MagicMock(return_value=mock_api_response)

    # Достаем скрытый объект __connect независимо от name mangling и подменяем его метод get
    connect_client = getattr(api, f"_{api.__class__.__name__}__connect")
    monkeypatch.setattr(connect_client, "get", mock_client_get)

    # 4. Выполняем тестируемый метод
    result = api.get_data("Spain")

    # 5. Проверки (Assertions)
    # Проверяем, что OpenStreetAPI получил правильную страну
    mock_get_coordinates.assert_called_once_with(country="Spain")

    # Проверяем, что APIClient.get вызван с правильным эндпоинтом и координатами
    mock_client_get.assert_called_once_with(
        endpoint="states/all",
        params={"lamin": 36.0, "lamax": 43.8, "lomin": -9.3, "lomax": 3.3}
    )

    # Проверяем, что Pydantic успешно распарсил ответ в модель
    assert isinstance(result, AeroplanesDB)
