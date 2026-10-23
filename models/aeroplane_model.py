from pydantic import model_validator
from typing import Any
from models.base_models import BaseAeroModel

class Aeroplane(BaseAeroModel):
    """Класс для хранения одной сущности аэроплана"""
    callsign: str
    """Позывной"""
    country_registry: str
    """Страна регистрации"""
    geo_altitude: float
    """Геометрическая высота"""
    on_ground: bool
    """Флаг нахождения на земле"""
    velocity: float
    """Горизонтальная скорость (м/с)"""

    def __str__(self) -> str:
        status = "✈️ В полете" if not self.on_ground else "🛑 На земле"

        # Шапка и тело для одного самолета
        header = f"┌{'─'*12} ДАННЫЕ О БОРТЕ [{self.callsign}] {'─'*12}┐"
        body = (
            f"│ Страна рег.: {self.country_registry}\n"
            f"│ Высота:      {self.geo_altitude} м\n"
            f"│ Скорость:    {self.velocity} м/с\n"
            f"│ Статус:      {status}"
        )
        footer = f"└{'─'*43}┘"

        return f"{header}\n{body}\n{footer}"

class AeroplanesDB(BaseAeroModel):
    """Хранение объектов по каждому самолёту"""

    data: list[Aeroplane]

    @model_validator(mode="before")
    @classmethod
    def transform_raw_list(cls, data: Any) -> Any:
        # Если на вход пришел напрямую список списков (например, db = AeroplanesDB(raw_data))
        if isinstance(data, list):
            raw_list = data
        # Если передали по именованному аргументу (например, db = AeroplanesDB(data=raw_data))
        elif isinstance(data, dict) and isinstance(data.get("data"), list):
            raw_list = data["data"]
        else:
            return data  # Возвращаем как есть, если структура иная, для стандартной обработки ошибок

        # Проверяем, что внутри действительно списки, а не готовые объекты Aeroplane
        if raw_list and isinstance(raw_list[0], list):
            transformed = []
            for item in raw_list:
                if item[14] is not None and item[8] is False:
                    transformed.append(
                        {
                            "callsign": item[1].strip() if isinstance(item[1], str) else item[1],
                            "country_registry": item[2],
                            "geo_altitude": item[14],
                            "on_ground": item[8],
                            "velocity": item[9],
                        }
                    )
            return {"data": transformed}

        return data

    def get_top_filtered_planes(
            self,
            country_match: str,
            altitude_str: str,
            top_n: int,
    ) -> list[Aeroplane]:
        """Фильтрует самолеты по условиям и возвращает Топ-N по убыванию geo_altitude"""

        # Парсим диапазон высот (например, "100000 - 150000" или "0-5000")
        try:
            min_alt, max_alt = map(float, altitude_str.split("-"))
        except ValueError:
            print("Ошибка: Неверный формат диапазона высот. Используется от 0 до бесконечности.")
            min_alt, max_alt = 0.0, float("inf")

        filtered_planes = []

        # Приводим строки к нижнему регистру для регистронезависимого поиска
        country_match_lower = country_match.strip().lower()

        for plane in self.data:
            plane_country = plane.country_registry.lower()

            # 1. Фильтр: Страна должна совпадать (если введена)
            if country_match_lower and country_match_lower != plane_country:
                continue

            # 2. Фильтр: Попадание в диапазон высот
            if not (min_alt <= plane.geo_altitude <= max_alt):
                continue

            filtered_planes.append(plane)

        # Сортируем по geo_altitude (по убыванию: от самых высоких к низким)
        filtered_planes.sort(key=lambda p: p.geo_altitude, reverse=True)

        # Возвращаем только топ N элементов
        return filtered_planes[:top_n]

    def __str__(self) -> str:
        if not self.data:
            return (
                "╔═════════════════════════════════════════════════╗\n"
                "║       БАЗА ДАННЫХ АЭРОПЛАНОВ ПУСТА              ║\n"
                "╚═════════════════════════════════════════════════╝"
                "\n"
            )

        # Главная общая шапка для всей базы данных
        main_header = (
            "=====================================================\n"
            f"  БАЗА ДАННЫХ АЭРОПЛАНОВ | Всего бортов в системе: {len(self.data)}\n"
            "====================================================="
        )

        # Собираем строковое представление для каждого самолета
        planes_str = []
        for idx, plane in enumerate(self.data, 1):
            # Добавляем порядковый номер перед каждым самолетом
            planes_str.append(f" Борт №{idx}:\n{plane}")

        return main_header + "\n" + "\n".join(planes_str) + "\n"