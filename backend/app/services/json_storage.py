from backend.app.services.database import SessionLocal
from backend.app.services.models import User, Ride
import json


# ---------------- USERS ---------------- #

def load_users():

    db = SessionLocal()
    users = db.query(User).all()
    db.close()

    result = []

    for u in users:
        result.append({
            "email": u.email,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "dob": u.dob,
            "contact": u.contact,
            "password": u.password,
            "security_q1": u.security_q1,
            "security_a1": u.security_a1,
            "security_q2": u.security_q2,
            "security_a2": u.security_a2,
            "active_ride_id": u.active_ride_id
        })

    return result


def save_users(users):

    db = SessionLocal()

    db.query(User).delete()

    for u in users:

        user = User(
            email=u["email"],
            first_name=u["first_name"],
            last_name=u["last_name"],
            dob=u["dob"],
            contact=u["contact"],
            password=u["password"],
            security_q1=u["security_q1"],
            security_a1=u["security_a1"],
            security_q2=u["security_q2"],
            security_a2=u["security_a2"],
            active_ride_id=u["active_ride_id"]
        )

        db.add(user)

    db.commit()
    db.close()


# ---------------- RIDES ---------------- #

def load_rides():

    db = SessionLocal()
    rides = db.query(Ride).all()
    db.close()

    result = []

    for r in rides:

        result.append({
            "ride_id": r.ride_id,
            "creator_email": r.creator_email,
            "from": r.from_location,
            "to": r.to_location,
            "time": r.time,
            "seats_total": r.seats_total,
            "seats_available": r.seats_available,
            "joined_users": json.loads(r.joined_users or "[]"),
            "pending_requests": json.loads(r.pending_requests or "[]"),
            "messages": json.loads(r.messages or "[]")
          
        })

    return result


def save_rides(rides):

    db = SessionLocal()

    db.query(Ride).delete()

    for r in rides:

        ride = Ride(
            ride_id=r["ride_id"],
            creator_email=r["creator_email"],
            from_location=r["from"],
            to_location=r["to"],
            time=r["time"],
            seats_total=r["seats_total"],
            seats_available=r["seats_available"],
            joined_users=json.dumps(r["joined_users"]),
            pending_requests=json.dumps(r["pending_requests"]),
            messages=json.dumps(r["messages"])
           
        )

        db.add(ride)

    db.commit()
    db.close()