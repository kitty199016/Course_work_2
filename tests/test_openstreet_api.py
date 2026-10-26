import pytest
from unittest.mock import MagicMock, patch
from models.streetmap_models import OpenStreetDataCoordinates

from src.openstreet_api import OpenStreetAPI


@pytest.fixture
def mock_api_client():
    """Фикстура для изоляции APIClient внутри OpenStreetAPI"""
    with patch("src.openstreet_api.APIClient") as MockClient:
        # Получаем mock-объект, который возвращается при вызове APIClient()
        client_instance = MockClient.return_value
        yield client_instance


def test_get_data_success(mock_api_client):
    """Тест успешного запроса координат страны и валидации модели"""
    # 1. Задаем фейковый ответ от Nominatim API
    # Nominatim возвращает список словарей. Нам нужен ключ 'boundingbox' у первого элемента.
    mock_api_client.get.return_value = [
        {
            "place_id": 123456,
            "licence": "Data © OpenStreetMap contributors",
            "boundingbox": ["55.0", "56.0", "37.0", "38.0"],  # Передается в model_validate
            "lat": "55.5",
            "lon": "37.5",
            "display_name": "Russia",
            "class": "boundary",
            "type": "administrative",
            "importance": 0.9
        }
    ]

    # 2. Инициализируем тестируемый API класс
    api = OpenStreetAPI()

    # 3. Вызываем метод
    result = api.get_data("Russia")

    # 4. Проверки (Assertions)
    # Проверяем, что APIClient.get вызван с правильными параметрами
    mock_api_client.get.assert_called_once_with(
        endpoint="search",
        params={
            'country': "Russia",  # Проверяем, что страна подставилась
            'format': 'json',
            'limit': 1,
        },
        headers={'User-Agent': 'test-app/1.0'}
    )

    # Проверяем, что метод вернул валидный объект pydantic-модели
    assert isinstance(result, OpenStreetDataCoordinates)


def test_get_data_empty_response(mock_api_client):
    """Тест поведения системы, если API вернул пустой список (страна не найдена)"""
    # Имитируем ситуацию, когда по запросу ничего не найдено
    mock_api_client.get.return_value = []

    api = OpenStreetAPI()

    # Проверяем, что код упадет с ошибкой IndexError (так как в коде прописано data[0])
    with pytest.raises(IndexError):
        api.get_data("NonexistentCountry")
