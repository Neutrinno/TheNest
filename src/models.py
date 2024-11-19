from pydantic import EmailStr
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

    information = relationship("Information", backref="user", uselist=False)
    assignments = relationship("Assignment", backref="user")
    applications = relationship("Application", backref="user")
    status_updates = relationship("Status", backref="user")
    roommate_preferences = relationship("RoommatePreference", backref="user")


class Information(Base):
    __tablename__ = "information"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    admission_score = Column(Integer, nullable=False)


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

    # Relationships
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
    full_name = Column(String, nullable=False)
    preferred_dormitory_id = Column(Integer)
    preferred_floor = Column(Integer)
    submission_date = Column(TIMESTAMP, nullable=False)

    roommate_preferences = relationship("RoommatePreference", backref="application")
    status_updates = relationship("Status", backref="application")


class Status(Base):
    __tablename__ = "status"

    application_id = Column(Integer, ForeignKey("application.id"), primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, nullable=False)


class RoommatePreference(Base):
    __tablename__ = "roommate_preference"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    preferred_student = Column(String, nullable=False)