from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, update
from sqlalchemy.exc import SQLAlchemyError

from app.db.orm import PersonORM
from app.models.person import Person


class PersonRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, notion_id):
        result = await self.session.execute(select(PersonORM).filter_by(notion_id=notion_id))
        return result.scalars().first()

    async def create(self, data: Person):
        new_person = PersonORM(**data.dict())
        self.session.add(new_person)
        try:
            await self.session.commit()
            await self.session.refresh(new_person)
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e
        return new_person

    async def update(self, notion_id, data: Person):
        await self.session.execute(
            update(PersonORM).
            where(PersonORM.notion_id == notion_id).
            values(**data.dict())
        )
        await self.session.commit()

    async def delete(self, notion_id):
        await self.session.execute(
            delete(PersonORM).
            where(PersonORM.notion_id == notion_id)
        )
        await self.session.commit()

    async def retrieve(self, notion_id: str) -> Person | None:
        result = await self.session.execute(select(PersonORM).filter_by(notion_id=notion_id))
        person = result.scalars().first()
        if person:
            return Person.from_orm(person)
        return None

    async def retrieve_many(self, filters) -> list[Person]:
        result = await self.session.execute(select(PersonORM).filter_by(**filters))
        persons = result.scalars().all()
        return [Person.from_orm(person) for person in persons]
