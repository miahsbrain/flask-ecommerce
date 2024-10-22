from project.extensions.dependencies import db, bcrypt
from project.models.base import BaseModel
from project.models.products import *
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Text
from flask_login import UserMixin
from sqlalchemy.orm import relationship, backref


class User(BaseModel, UserMixin):
    __tablename__ = 'users'
    uid = Column(Integer, autoincrement=True, unique=True, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    phone = Column(String(100), nullable=True)
    password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    profile_picture = relationship("ProfilePicture", backref=backref('user'), uselist=False, cascade='all, delete-orphan')
    products = relationship('Product', backref='user', lazy=True)
    cart = relationship('Cart', backref='user', uselist=False, lazy=True)
    orders = relationship('Order', backref='user', lazy=True)
    payments = relationship('Payment', backref='user', lazy=True)
    shipping_address = relationship('ShippingAddress', backref='user', uselist=False, lazy=True)

    def __repr__(self) -> str:
        return f'<NAME: {self.first_name} {self.last_name}, EMAIL: {self.email}>'
    
    def get_id(self):
        return self.uid
    
    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'
    
    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)
    
    def check_password(self, password):
        return True if bcrypt.check_password_hash(password, self.password) else False
    
    def get_profile_picture_url(self):
        return str(self.profile_picture.url) if self.profile_picture else 'https://via.placeholder.com/120'

class ProfilePicture(BaseModel):
    __tablename__ = 'profile_pictures'
    id = Column(Integer, autoincrement=True, unique=True, primary_key=True)
    url = Column(String())
    user_id = Column(String(), ForeignKey('users.uid', name='fk_profile_pictures_user'))

    def __repr__(self):
        return f'<URL: {self.url}, USER: {self.user_id}>'

class AnonymousUser(UserMixin):
    uid = '10000000001'
    first_name = 'Anonymous'
    last_name = 'User'
    email = 'anonymoususer@anonymous.com'
    is_authenticated = False
    password = 'unsafe-password'

    def __repr__(self) -> str:
        return f'<NAME: {self.first_name} {self.last_name}, EMAIL: {self.email}>'
    
    def get_id(self):
        return self.uid
    
    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'
    
    def set_password(self):
        pass
    
    def check_password(self):
        return True
    
    def get_profile_picture_url(self):
        return 'https://via.placeholder.com/120'