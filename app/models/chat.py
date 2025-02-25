from sqlmodel import SQLModel, Field


class Chat(SQLModel, table=True):
    chat_id: int = Field(default=None, primary_key=True)
    user_id: int = Field(
        default=None, foreign_key="user.user_id", ondelete="CASCADE"
    )
    name: str | None = None

    # user: "User" = Relationship(back_populates="chats")
    # predictions: list["Prediction"] = Relationship(
    #     back_populates="chat", cascade_delete=True
    # )

    # @property
    # def user_id(self) -> int:
    #     return self.user_id

    # @property
    # def name(self) -> str:
    #     return self.name

    # @name.setter
    # def name(self, name) -> None:
    #     self.name = name
