from sqlalchemy import Table, Column, String, Integer, MetaData
from sqlalchemy.orm import mapper, Session

from . import EntityID
from .exceptions import NotFound
from .service import Repository
from .entity import EntityDTO, Entity

meta = MetaData()

entities_t: Table = Table(
    'entities',
    meta,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('uuid', String, unique=True, index=True),
    Column('value', String, nullable=True),
)

EntityMapper = mapper(
    EntityDTO,
    entities_t,
    properties={
        'id': entities_t.c.uuid,
        'value': entities_t.c.value,
    },
    column_prefix='_db_column_',
)


class ORMRepository(Repository):
    def __init__(self, session: Session):
        self._session = session
        self._query = self._session.query(EntityMapper)

    def get(self, entity_id: EntityID) -> Entity:
        dto = self._query.filter_by(uuid=entity_id).one_or_none()
        if not dto:
            raise NotFound(entity_id)
        return Entity(dto)

    def save(self, entity: Entity) -> None:
        self._session.add(entity.dto)
        self._session.flush()
