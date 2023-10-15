from app import app
from models import db, User

db.drop_all()
db.create_all()

u1 = User(
    username = "hello",
    password = "world",
    email = "abc@123.com",
    first_name = "hello",
    last_name = "world",
  )

db.session.add(u1)
db.session.commit()