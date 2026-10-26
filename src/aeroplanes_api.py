from src.api_client import APIClient
from src.base_adapters import AeroAPI
from src.openstreet_api import OpenStreetAPI
from models.aeroplane_model import AeroplanesDB

class AeroplaneAPI(AeroAPI):
    """Класс для взаимодействия с open street map"""

    def __init__(self):
        base_url = 'https://opensky-network.org/api'
        self.__connect = APIClient(base_url=base_url)
        self.__headers_nominatim = {'User-Agent': 'test-app/1.0'}
        self.__params_nominatim = {
            'country': "",
            'format': 'json',
            'limit': 1,
        }
        self.coordinates = OpenStreetAPI()

    def get_data(self, country: str) -> AeroplanesDB:
        """
        :param country: Принимает страну
        по которым выдаст самолёты пролетающие над этой страной
        :return: Список самолётов, пролетающих над этиой страной
        """
        endpoint = "states/all"
        params = self.coordinates.get_data(country=country)
        data = self.__connect.get(endpoint=endpoint,
                                  params=params.model_dump())

        return AeroplanesDB.model_validate(data['states'])

if __name__ == '__main__':
    a = AeroplaneAPI()
    print(a.get_data("Spain"))
