from src.aeroplanes_api import AeroplaneAPI
from src.manager import AeroplaneRepositoryFactory

# Функция для взаимодействия с пользователем
def user_interaction():
    country = input("Введите название страны: ")
    top_n = int(input("Введите количество самолетов для вывода в топ N: "))
    country_registry = input("Введите названия стран для фильтрации по стране регистрации: ")
    altitude_range = input("Введите диапазон высот полета: ") # Пример: 100000 - 150000

    aeroplane_api = AeroplaneAPI()

    aeroplanes_in_country = aeroplane_api.get_data(country)

    for aeroplane in aeroplanes_in_country.get_top_filtered_planes(country_match=country_registry,
                                                        altitude_str=altitude_range,
                                                        top_n=top_n
                                                        ):
        print(aeroplane)

    write_to_file = input("Записать в файл?[Y/n]:")
    if write_to_file in {"Y", "yes", "y"}:

        file_type = input("Введите тип файла[json/csv]:")
        file_repo = AeroplaneRepositoryFactory.create_repository(f"data/aerplanes.{file_type}")
        file_repo.save(aeroplanes_in_country)


if __name__ == "__main__":
    user_interaction()