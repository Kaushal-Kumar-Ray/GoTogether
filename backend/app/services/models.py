from sqlalchemy import Column, String, Integer, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    email = Column(String, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    dob = Column(String)
    contact = Column(String)
    password = Column(String)

    security_q1 = Column(String)
    security_a1 = Column(String)

    security_q2 = Column(String)
    security_a2 = Column(String)

    active_ride_id = Column(String)


class Ride(Base):
    __tablename__ = "rides"

    ride_id = Column(String, primary_key=True)

    creator_email = Column(String)

    from_location = Column(String)
    to_location = Column(String)

    time = Column(String)

    seats_total = Column(Integer)
    seats_available = Column(Integer)

    joined_users = Column(Text)
    pending_requests = Column(Text)
    messages = Column(Text)