from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from db_models.database import Base, Session
import datetime

class DBLogger(Base):
    
    __tablename__ = "logger_refresh_table"
    
    # ! PK
    log_id = Column(Integer, primary_key=True, autoincrement=True)
    # ! FK
    operation_id = Column(Integer, ForeignKey("list_table_operations.operation_id"))
    # ! fields
    table_name = Column(String, nullable=True)
    time = Column(DateTime, nullable=False)
    
    def __init__(self, 
                 table_name: str, 
                 operation_id: int, 
                 time: datetime.datetime) -> None:
        
        self.table_name = table_name
        self.operation_id = operation_id
        self.time = time

    def __repr__(self) -> str:
        return f"DBLogger(table_name={self.table_name}, operation_id={self.operation_id}, refresh_time={self.refresh_time})"


def add_sql_log(session: Session, data: DBLogger) -> None:
    session.add(data)
    session.commit()
    session.close() 
 