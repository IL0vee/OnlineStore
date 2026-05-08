from flask_marshmallow import Marshmallow
from marshmallow import fields, validate, ValidationError, pre_load
from app.models import User, Post, Category, Tag, Comment
import re

ma = Marshmallow()

# Валидаторы
def validate_username(username):
    """Проверка username: 3-30 символов, только буквы, цифры, подчеркивание"""
    if not (3 <= len(username) <= 30):
        raise ValidationError('Username должен быть от 3 до 30 символов')
    if not re.match(r'^[a-zA-Z0-9_а-яА-Я]+$', username):
        raise ValidationError('Username может содержать только буквы, цифры и подчеркивание')

def validate_password(password):
    """Проверка пароля: минимум 6 символов"""
    if len(password) < 6:
        raise ValidationError('Пароль должен быть не менее 6 символов')

class UserRegistrationSchema(ma.Schema):
    """Схема для регистрации пользователя"""
    username = fields.String(required=True, validate=validate_username)
    password = fields.String(required=True, validate=validate_password)
    full_name = fields.String(required=False, allow_none=True)

class UserLoginSchema(ma.Schema):
    """Схема для входа пользователя"""
    username = fields.String(required=True)
    password = fields.String(required=True)

class UserSchema(ma.SQLAlchemyAutoSchema):
    """Схема для вывода информации о пользователе"""
    class Meta:
        model = User
        include_relationships = True
        load_instance = True
        exclude = ('password',)  # Не выводим пароль

class CategorySchema(ma.SQLAlchemyAutoSchema):
    """Схема для категорий"""
    class Meta:
        model = Category
        load_instance = True

class TagSchema(ma.SQLAlchemyAutoSchema):
    """Схема для тегов"""
    class Meta:
        model = Tag
        load_instance = True

class CommentSchema(ma.SQLAlchemyAutoSchema):
    """Схема для комментариев"""
    class Meta:
        model = Comment
        load_instance = True
    
    author = fields.Nested(UserSchema, dump_only=True)

class PostCreateSchema(ma.Schema):
    """Схема для создания и обновления поста"""
    title = fields.String(required=True, validate=validate.Length(min=3, max=200))
    content = fields.String(required=True, validate=validate.Length(min=10))
    id_category = fields.Integer(required=False, allow_none=True)
    id_tag = fields.Integer(required=False, allow_none=True)
    status = fields.String(required=False, allow_none=True, 
                          validate=validate.OneOf(['draft', 'published', 'archived']))

class PostSchema(ma.SQLAlchemyAutoSchema):
    """Схема для вывода информации о посте"""
    class Meta:
        model = Post
        load_instance = True
    
    author = fields.Nested(UserSchema, dump_only=True)
    category = fields.Nested(CategorySchema, dump_only=True)
    tag = fields.Nested(TagSchema, dump_only=True)
    comments = fields.Nested(CommentSchema, many=True, dump_only=True)

class CommentCreateSchema(ma.Schema):
    """Схема для создания комментария"""
    text = fields.String(required=True, validate=validate.Length(min=1, max=1000))
