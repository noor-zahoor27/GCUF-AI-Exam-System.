from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    roll_no = Column(String, unique=True)
    name = Column(String)
    dept = Column(String)

class Hall(Base):
    __tablename__ = "halls"
    id = Column(Integer, primary_key=True, index=True)
    hall_name = Column(String)
    rows = Column(Integer)
    cols = Column(Integer)

class SeatingAssignment(Base):
    __tablename__ = "seating_assignments"
    id = Column(Integer, primary_key=True, index=True)
    student_name = Column(String)
    student_dept = Column(String)
    hall_name = Column(String)
    seat_label = Column(String)
