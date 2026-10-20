from abc import abstractmethod, ABC
from typing import Generic, TypeVar

class BaseModel: pass

T_model = TypeVar('T_model', bound=BaseModel, covariant=True)

class ClientAPI(ABC, Generic[T_model]):
    """Основной клиент для запросов """

    @abstractmethod
    def get_data(self):...