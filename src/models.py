from sqlalchemy import  Column, Integer, String, TIMESTAMP, ForeignKey, Boolean, func
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    registered_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    hashed_password = Column(String(length=1024), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    assignments = relationship("Assignment", backref="user")
    applications = relationship("Application", backref="user")
    status_updates = relationship("Status", backref="user")


class Dormitory(Base):
    __tablename__ = "dormitory"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    filled = Column(String, nullable=False)

    rooms = relationship("Room", backref="dormitory")


class Room(Base):
    __tablename__ = "room"

    id = Column(Integer, primary_key=True)
    dormitory_id = Column(Integer, ForeignKey("dormitory.id"))
    room_number = Column(String, nullable=False)
    floor = Column(Integer, nullable=False)
    capacity = Column(Integer, nullable=False)
    filled = Column(Boolean, default=False, nullable=False)

    beds = relationship("Bad", backref="room")


class Bad(Base):
    __tablename__ = "bad"

    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey("room.id"))
    is_occupied = Column(Boolean, default=False, nullable=False)

    assignments = relationship("Assignment", backref="bed")


class Assignment(Base):
    __tablename__ = "assignment"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    bad_id = Column(Integer, ForeignKey("bad.id"))
    application_status = Column(String, nullable=False)

class Application(Base):
    __tablename__ = "application"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    first_name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    middle_name = Column(String)
    admission_score = Column(Integer, nullable=False)
    preferred_dormitory = Column(Integer)
    preferred_floor = Column(Integer)
    submission_date = Column(TIMESTAMP, nullable=False)
    first_preferred_student = Column(String)
    second_preferred_student = Column(String)
    third_preferred_student = Column(String)

    status_updates = relationship("Status", backref="application")

class Status(Base):
    __tablename__ = "status"

    application_id = Column(Integer, ForeignKey("application.id"), primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, nullable=False)

class StudentListing(Base):
    __tablename__ = "student_listing"

    id = Column(Integer, primary_key=True)
    admission_score = Column(Integer, nullable=False)
