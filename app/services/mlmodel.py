from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class MLModel:
    # или другой тип, смотря, что будет в бд
    __id: int = field(default=None, init=False)
    __model: Any = field(default=None, init=False)

    def init_model(self) -> Any:
        """Загружает модель в систему. Пока не ясно"""
        pass

    def predict(request: str) -> str:
        # __model.predict()
        pass
