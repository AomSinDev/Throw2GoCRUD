from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import firebase_admin
from firebase_admin import credentials, db

# Init Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://throw2go-ae7b1-default-rtdb.asia-southeast1.firebasedatabase.app"  # แก้เป็นของคุณ
})

app = FastAPI()

# ----------------- Models ----------------- #
class UserCreate(BaseModel):
    name: str
    points: int = 0

class PointUpdate(BaseModel):
    points: int

# ----------------- Routes ----------------- #

# CREATE user
@app.post("/users")
def create_user(user: UserCreate):
    ref = db.reference("users")
    new_user = ref.push({
        "name": user.name,
        "points": user.points
    })
    return {"message": "User created", "user_id": new_user.key}

# READ all users
@app.get("/users")
def get_users():
    ref = db.reference("users")
    users = ref.get()
    return users or {}

# UPDATE: add points
@app.patch("/users/{user_id}/add_points")
def add_points(user_id: str, update: PointUpdate):
    user_ref = db.reference(f"users/{user_id}")
    user = user_ref.get()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    new_points = user.get("points", 0) + update.points
    user_ref.update({"points": new_points})
    return {"message": "Points updated", "new_points": new_points}

# DELETE user
@app.delete("/users/{user_id}")
def delete_user(user_id: str):
    user_ref = db.reference(f"users/{user_id}")
    if not user_ref.get():
        raise HTTPException(status_code=404, detail="User not found")
    user_ref.delete()
    return {"message": "User deleted"}
