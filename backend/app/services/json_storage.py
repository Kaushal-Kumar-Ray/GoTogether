from backend.app.services.database import SessionLocal
from backend.app.services.models import User, Ride
import json

def load_users():
    db = SessionLocal()
    users = db.query(User).all()
    db.close()

    return [u.__dict__ for u in users]


def save_users(users):
    db = SessionLocal()

    db.query(User).delete()

    for u in users:
        user = User(**u)
        db.add(user)

    db.commit()
    db.close()


def load_rides():
    db = SessionLocal()
    rides = db.query(Ride).all()
    db.close()

    result = []

    for r in rides:
        ride = r.__dict__

        ride["joined_users"] = json.loads(r.joined_users or "[]")
        ride["pending_requests"] = json.loads(r.pending_requests or "[]")
        ride["messages"] = json.loads(r.messages or "[]")

        result.append(ride)

    return result


def save_rides(rides):
    db = SessionLocal()

    db.query(Ride).delete()

    for r in rides:
        ride = Ride(
            ride_id=r["ride_id"],
            creator_email=r["creator_email"],
            from_location=r["from_location"],
            to_location=r["to_location"],
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