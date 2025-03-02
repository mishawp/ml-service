from sqlmodel import Session, select
from dataclasses import dataclass
from models.chat import Chat


@dataclass(slots=True)
class ChatService:
    session: Session

    def create_one(self, chat: Chat) -> Chat:
        self.session.add(chat)
        self.session.commit()
        self.session.refresh(chat)
        return chat

    def read_by_id(self, chat_id: int) -> Chat:
        chat = self.session.get(Chat, chat_id)
        return chat if chat else None

    def read_by_user_id(self, user_id: int) -> list[Chat]:
        return self.session.exec(
            select(Chat).where(Chat.user_id == user_id)
        ).all()

    def read_user_chat(self, chat_id: int, user_id: int) -> Chat:
        return self.session.exec(
            select(Chat).where(
                Chat.chat_id == chat_id and Chat.user_id == user_id
            )
        ).first()

    def read_all(self) -> list[Chat]:
        return self.session.exec(select(Chat)).all()

    def update_by_id(self, chat_id: int, **kwargs) -> Chat:
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

    def delete_by_id(self, chat_id: int) -> Chat:
        chat = self.session.get(Chat, chat_id)
        if not chat:
            raise ValueError(f"Chat with id {chat_id} not found")

        self.session.delete(chat)
        self.session.commit()
        return chat
