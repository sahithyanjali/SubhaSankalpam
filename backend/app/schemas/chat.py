from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.models.chat import ChatRoomStatus, MessageType


class CreateChatRoom(BaseModel):
    user2_id: UUID
    match_id: Optional[UUID] = None


class SendMessage(BaseModel):
    content: str
    message_type: MessageType = MessageType.TEXT


class ChatMessageResponse(BaseModel):
    id: UUID
    room_id: UUID
    sender_id: UUID
    content: str
    message_type: MessageType
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatRoomResponse(BaseModel):
    id: UUID
    user1_id: UUID
    user2_id: UUID
    status: ChatRoomStatus
    last_message: Optional[ChatMessageResponse] = None
    unread_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatRoomListResponse(BaseModel):
    rooms: list[ChatRoomResponse]
    total: int
