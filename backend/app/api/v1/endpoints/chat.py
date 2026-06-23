from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.middleware.auth import get_current_active_user
from app.models.chat import ChatMessage, ChatRoom, ChatRoomStatus
from app.models.notification import Notification, NotificationType
from app.models.user import User
from app.schemas.chat import (
    ChatMessageResponse,
    ChatRoomListResponse,
    ChatRoomResponse,
    SendMessage,
)

router = APIRouter(prefix="/chat", tags=["Chat"])


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: str):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)

    def disconnect(self, websocket: WebSocket, room_id: str):
        if room_id in self.active_connections:
            self.active_connections[room_id].remove(websocket)

    async def broadcast(self, room_id: str, message: dict):
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                await connection.send_json(message)


manager = ConnectionManager()


@router.get("/rooms", response_model=ChatRoomListResponse)
async def get_chat_rooms(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get all chat rooms for the current user."""
    result = await db.execute(
        select(ChatRoom).where(
            or_(ChatRoom.user1_id == current_user.id, ChatRoom.user2_id == current_user.id)
        ).order_by(ChatRoom.updated_at.desc())
    )
    rooms = result.scalars().all()

    room_responses = []
    for room in rooms:
        # Get last message
        last_msg_result = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.room_id == room.id)
            .order_by(ChatMessage.created_at.desc())
            .limit(1)
        )
        last_msg = last_msg_result.scalar_one_or_none()

        # Get unread count
        unread_result = await db.execute(
            select(func.count(ChatMessage.id)).where(
                and_(
                    ChatMessage.room_id == room.id,
                    ChatMessage.sender_id != current_user.id,
                    ChatMessage.is_read.is_(False),
                )
            )
        )
        unread_count = unread_result.scalar()

        room_resp = ChatRoomResponse(
            id=room.id,
            user1_id=room.user1_id,
            user2_id=room.user2_id,
            status=room.status,
            last_message=last_msg if last_msg else None,
            unread_count=unread_count,
            created_at=room.created_at,
        )
        room_responses.append(room_resp)

    return ChatRoomListResponse(rooms=room_responses, total=len(room_responses))


@router.get("/rooms/{room_id}/messages")
async def get_messages(
    room_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get messages in a chat room."""
    # Verify user is in the room
    room_result = await db.execute(select(ChatRoom).where(ChatRoom.id == room_id))
    room = room_result.scalar_one_or_none()
    if not room or (room.user1_id != current_user.id and room.user2_id != current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")

    # Mark messages as read
    await db.execute(
        update(ChatMessage)
        .where(
            and_(
                ChatMessage.room_id == room_id,
                ChatMessage.sender_id != current_user.id,
                ChatMessage.is_read.is_(False),
            )
        )
        .values(is_read=True)
    )

    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.room_id == room_id)
        .order_by(ChatMessage.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    messages = result.scalars().all()
    await db.commit()

    return {
        "messages": [
            {
                "id": str(m.id),
                "sender_id": str(m.sender_id),
                "content": m.content,
                "message_type": m.message_type.value,
                "is_read": m.is_read,
                "created_at": m.created_at.isoformat(),
            }
            for m in reversed(messages)
        ]
    }


@router.post("/rooms/{room_id}/messages", response_model=ChatMessageResponse)
async def send_message(
    room_id: UUID,
    data: SendMessage,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Send a message in a chat room."""
    room_result = await db.execute(select(ChatRoom).where(ChatRoom.id == room_id))
    room = room_result.scalar_one_or_none()
    if not room or (room.user1_id != current_user.id and room.user2_id != current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")

    if room.status != ChatRoomStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Chat room is not active")

    message = ChatMessage(
        room_id=room_id,
        sender_id=current_user.id,
        content=data.content,
        message_type=data.message_type,
    )
    db.add(message)

    # Notify the other user
    other_user_id = room.user2_id if room.user1_id == current_user.id else room.user1_id
    notification = Notification(
        user_id=other_user_id,
        notification_type=NotificationType.NEW_MESSAGE,
        title="New Message",
        body="You have a new message.",
    )
    db.add(notification)

    await db.commit()
    await db.refresh(message)

    # Broadcast via WebSocket
    await manager.broadcast(
        str(room_id),
        {
            "id": str(message.id),
            "sender_id": str(message.sender_id),
            "content": message.content,
            "message_type": message.message_type.value,
            "created_at": message.created_at.isoformat(),
        },
    )

    return message


@router.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    """WebSocket for real-time chat."""
    await manager.connect(websocket, room_id)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast(room_id, data)
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
