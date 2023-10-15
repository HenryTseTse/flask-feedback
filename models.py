from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    """Connect DB"""
    db.app = app
    db.init_app(app)


class User(db.Model):
    """User Model"""

    __tablename__ = "users"

    username = db.Column(db.String(20), primary_key=True, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    feedback = db.relationship("Feedback", backref="user")
    
    @classmethod
    def register(cls, username, password, email, first_name, last_name):
        """Register User"""

        hashed = bcrypt.generate_password_hash(password) # Turn bytestring into unicode utf8 string
        hashed_utf8 = hashed.decode("utf8")
        user = cls(username=username,
                   password=hashed_utf8,
                   first_name=first_name,
                   last_name=last_name,
                   email=email
        )
        db.session.add(user)
        return user
    
    @classmethod
    def authenticate(cls, username, password):
        """Validate User"""

        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, password):
            return u
        else:
            return False
        
class Feedback(db.Model):
    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    username = db.Column(db.Text, db.ForeignKey("users.username"))
