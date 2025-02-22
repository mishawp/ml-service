from sqlmodel import Session
from dataclasses import dataclass
from models.chat import Chat


@dataclass(slots=True)
class ChatService:
    session: Session

    def create_chat(self, chat: Chat) -> Chat:
        self.session.add(chat)
        self.session.commit()
        self.session.refresh(chat)
        return chat

    def read_chat(self, chat_id: int) -> Chat:
        chat = self.session.get(Chat, chat_id)
        return chat if chat else None

    def update_chat(self, chat_id: int, **kwargs) -> Chat:
        chat = self.session.get(Chat, chat_id)
        if not chat:
            raise ValueError(f"Chat with id {chat_id} not found")

        for key, value in kwargs.items():
            if hasattr(chat, key):
                setattr(chat, key, value)
            else:
                raise AttributeError(f"Chat has no attribute {key}")

        self.session.add(chat)
        self.session.commit()
        self.session.refresh(chat)
        return chat

    def delete_chat(self, chat_id: int) -> Chat:
        chat = self.session.get(Chat, chat_id)
        if not chat:
            raise ValueError(f"Chat with id {chat_id} not found")

        self.session.delete(chat)
        self.session.commit()
        return chat

    # def open(self) -> list[Prediction]:
    #     pass

    # # может и не нужен
    # def close(self):
    #     pass
