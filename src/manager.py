import os
from abc import ABC, abstractmethod
from models.aeroplane_model import AeroplanesDB, Aeroplane
import orjson
import csv

class BaseAeroplaneRepository(ABC):

    def __init__(self, file_path: str):
        self.file_path = file_path

    @abstractmethod
    def load(self) -> AeroplanesDB:
        """Считать данные из файла в модель AeroplanesDB"""
        pass

    @abstractmethod
    def save(self, db: AeroplanesDB) -> None:
        """Сохранить модель AeroplanesDB в файл"""
        pass

    @abstractmethod
    def delete_by_callsign(self, callsign: str) -> bool:
        """Удалить самолет по позывному и обновить файл"""
        pass


# --- Конкретная реализация для JSON ---
class JsonAeroplaneRepository(BaseAeroplaneRepository):

    def load(self) -> AeroplanesDB:
        if not os.path.exists(self.file_path) or os.path.getsize(self.file_path) == 0:
            return AeroplanesDB(data=[])

        with open(self.file_path, "rb") as f:
            raw_json = orjson.loads(f.read())
            return AeroplanesDB.model_validate(raw_json)

    def save(self, db: AeroplanesDB) -> None:
        with open(self.file_path, "wb") as f:
            bytes_data = orjson.dumps(
                db.model_dump(mode="json"), option=orjson.OPT_INDENT_2
            )
            f.write(bytes_data)

    def delete_by_callsign(self, callsign: str) -> bool:
        db = self.load()
        initial_count = len(db.data)
        db.data = [
            p for p in db.data if p.callsign.strip() != callsign.strip()
        ]

        if len(db.data) < initial_count:
            self.save(db)
            return True
        return False


# --- Конкретная реализация для CSV ---
class CsvAeroplaneRepository(BaseAeroplaneRepository):
    # Поля заголовка CSV файла (извлекаются динамически из модели Aeroplane)
    CSV_FIELDS = list(Aeroplane.model_fields.keys())

    def load(self) -> AeroplanesDB:
        if not os.path.exists(self.file_path) or os.path.getsize(self.file_path) == 0:
            return AeroplanesDB(data=[])

        planes = []
        with open(self.file_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # csv всегда читает строки, Pydantic сам приведет их к float/bool
                planes.append(row)

        return AeroplanesDB(data=planes)

    def save(self, db: AeroplanesDB) -> None:
        with open(self.file_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.CSV_FIELDS)
            writer.writeheader()

            # Превращаем модели в JSON-совместимые словари для записи строк
            for plane in db.data:
                writer.writerow(plane.model_dump(mode="json"))

    def delete_by_callsign(self, callsign: str) -> bool:
        db = self.load()
        initial_count = len(db.data)
        db.data = [
            p for p in db.data if p.callsign.strip() != callsign.strip()
        ]

        if len(db.data) < initial_count:
            self.save(db)
            return True
        return False


# --- 5. Фабрика для создания репозиториев ---
class AeroplaneRepositoryFactory:

    @staticmethod
    def create_repository(file_path: str) -> BaseAeroplaneRepository:
        """Определяет формат по расширению файла и возвращает нужный драйвер"""
        _, ext = os.path.splitext(file_path.lower())

        if ext == ".json":
            return JsonAeroplaneRepository(file_path)
        elif ext == ".csv":
            return CsvAeroplaneRepository(file_path)
        else:
            raise ValueError(
                f"Неподдерживаемый формат файла: {ext}. Допустимы .json и .csv"
            )