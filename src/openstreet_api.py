from src.api_client import APIClient
from src.base_adapters import AeroAPI
from models.streetmap_models import OpenStreetDataCoordinates

class OpenStreetAPI(AeroAPI):
    """Класс для взаимодействия с open street map"""

    def __init__(self):
        base_url = 'https://nominatim.openstreetmap.org'
        self.__connect = APIClient(base_url=base_url)
        self.__headers_nominatim = {'User-Agent': 'test-app/1.0'}
        self.__params_nominatim = {
            'country': "",
            'format': 'json',
            'limit': 1,
        }

    def get_data(self, country: str) -> OpenStreetDataCoordinates:
        endpoint = "search"
        self.__params_nominatim["country"] = country
        data = self.__connect.get(endpoint=endpoint,
                                  params=self.__params_nominatim,
                                  headers=self.__headers_nominatim)
        return OpenStreetDataCoordinates.model_validate(data[0].get('boundingbox'))

if __name__ == '__main__':
    a = OpenStreetAPI()
    print(a.get_data("Russia"))