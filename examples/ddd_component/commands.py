from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from typing import Text
from uuid import UUID, uuid1

from .entity import EntityID

CommandID = UUID


class Command(ABC):
    entity_id: EntityID
    command_id: CommandID
    timestamp: datetime


@dataclass
class Create(Command):
    command_id: CommandID = field(default_factory=uuid1)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class UpdateValue(Command):
    entity_id: EntityID
    value: Text
    command_id: CommandID = field(default_factory=uuid1)
    timestamp: datetime = field(default_factory=datetime.utcnow)
