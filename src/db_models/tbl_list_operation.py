from typing import List
from sqlalchemy import Column, Integer, String
from db_models.database import Base, Session
from sqlalchemy.orm import relationship

class ListOperations(Base):
    
    __tablename__ = "list_table_operations"
    
    # ! PK
    operation_id = Column(Integer, primary_key=True, nullable=False)
    # ! fields
    operation_name = Column(String, nullable=False)
    
    list_operations = relationship("DBLogger", backref="list_operations")
    
    def __init__(self, operation_id: int, operation_name: str) -> None:

        self.operation_id = operation_id
        self.operation_name = operation_name
    
    def __repr__(self) -> str:
        return f"Operations(operation_id={self.operation_id}, operation_name={self.operation_name})"


def add_operations(session: Session) -> None:
    session.add_all([
        ListOperations(operation_id=1, operation_name="delete table"),
        ListOperations(operation_id=2, operation_name="create table"),
        ListOperations(operation_id=3, operation_name="add new data into table"),
        ListOperations(operation_id=4, operation_name="create database")
    ])
    session.commit()
    session.close()