from flask_login import UserMixin

from flask import session

class User(UserMixin):
    email: str
    def __init__(self, nome, senha):
        self.nome = nome
        self.senha = senha

    @classmethod
    def get(cls, user_id):
        usuarios = session.get('usuarios')
        if user_id in usuarios.keys():
            email = user_id
            senha = usuarios[user_id]

            user = User(email, senha)
            user.id = user_id
            return user

