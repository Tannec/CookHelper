import time
import jwt
from random import choice
from django.core.files.uploadedfile import UploadedFile
from django.db import models
from django.db.models import *
from werkzeug.security import *
import datetime
from cookhelper.settings import SECRET_KEY, STATICFILES_DIRS, MEDIA_ROOT, BASE_DIR
from api.views_model.static_functions import *


# models: Recipe, User, Forum, Ingredient, Dialog

def user_upload_to_path(instance, filename):
    return f'{MEDIA_ROOT}/users/{instance.id}/{filename}'


def recipe_upload_to_path(instance, filename):
    return f'{MEDIA_ROOT}/recipes/{instance.id}/{filename}'


def forum_upload_to_path(instance, filename):
    return f'{MEDIA_ROOT}/forum/{instance.id}/{filename}'


class User(models.Model, Type):
    name = CharField(max_length=40)
    surname = CharField(max_length=40)
    email = CharField(max_length=100, unique=True)
    nickname = CharField(max_length=100, default="", unique=True)
    avatar = ImageField(upload_to=user_upload_to_path, default="")
    last_seen = BigIntegerField(default=None)
    status = CharField(default="", max_length=200)

    password = TextField()
    token = CharField(max_length=512)
    deleted = BooleanField(default=False)
    verified = BooleanField(default=False)
    code = CharField(default="", max_length=6)
    recoveryCode = CharField(default="", max_length=5)

    fridge = TextField(default="")
    forums = TextField(default="")
    starredRecipes = TextField(default="")
    bannedRecipes = TextField(default="")
    starredIngredients = TextField(default="")
    bannedIngredients = TextField(default="")
    ownRecipes = TextField(default="")

    def __str__(self):
        return "email: " + self.email + " psw: " + self.password + " nick: " + self.nickname

    def setPassword(self, password):
        self.password = generate_password_hash(password)
        self.save()

    def validatePassword(self, password):
        return check_password_hash(self.password, password)

    def generateToken(self, data: dict):
        data['time'] = round(time.time() * 1000)
        data['prohodnoyeSlovoComrade'] = self.password
        tt = jwt.encode(data, SECRET_KEY, algorithm='HS256')
        self.token = tt
        self.save()

    def passwordAvailability(self, password):
        if len(password) < 8:
            raise ModelException(message='Password must be at least 8 symbols', status=109)
        with open(os.path.join(BASE_DIR, 'data\\rejected_passwords.p')) as t:
            passwords = t.readlines()
            for _ in passwords:
                if _ in password:
                    raise RejectException(message='Simple password', status=109)

    def loginAvailability(self, login):
        try:
            user = User.objects.get(Q(email=login) | Q(nickname=login))
            return False
        except Exception as e:
            return True

    def generateCode(self, length=6, type=Type.GENERAL):
        code = ""
        for i in range(length):
            code += str(choice(range(10)))
        if type == Type.GENERAL:
            self.code = code
        else:
            self.recoveryCode = code
        self.save()
        return code

    def verifyCode(self, code):
        if code == self.code:
            self.verified = True
            self.save()
        return self.verified

    def validateToken(self, token: str):
        return self.token == token

    def setAvatar(self, image: UploadedFile):
        self.avatar = image
        self.last_seen = round(time.time() * 1000)
        self.save()

    def validateData(self, data):
        fields = ['name',
                  'surname',
                  'email',
                  'password',
                  'nickname'
                  ]
        for i in data:
            if i not in fields:
                raise UnknownField(i)
            else:
                del fields[fields.index(i)]
        if fields:
            raise MissFields(fields)
        if not self.loginAvailability(data['email']):
            raise RejectException(field='email', status=108)
        if not self.loginAvailability(data['nickname']):
            raise RejectException(field='nickname', status=107)

    def getInfo(self, type) -> dict:
        try:
            dict = {}
            dict['id'] = self.id
            dict['status'] = self.status
            dict['name'] = self.name
            dict['nickname'] = self.nickname
            dict['email'] = self.email
            dict['surname'] = self.surname
            dict['avatar'] = self.avatar.name
            dict['verified'] = self.verified
            dict['lastSeen'] = self.last_seen
            if type == self.PRIVATE:
                self.last_seen = round(time.time() * 1000)
                self.save()
                dict['token'] = self.token
                dict['starredRecipes'] = self.starredRecipes
                dict['bannedRecipes'] = self.bannedRecipes
                dict['starredIngredients'] = self.starredIngredients
                dict['bannedIngredients'] = self.bannedIngredients
                dict['fridge'] = self.fridge
                dict['forums'] = self.forums
                dict['ownRecipes'] = []
                for id in self.ownRecipes.split():
                    recipe = Recipe.objects.get(id=int(id))
                    dict['ownRecipes'].append(recipe.getInfo())
            return dict
        except Exception as e:
            return {'message': str(e), 'status': -1}

    def register(self, data):
        self.validateData(data)
        self.passwordAvailability(password=data['password'])
        self.name = data['name']
        self.nickname = data['nickname']
        self.surname = data['surname']
        self.email = data['email']
        self.last_seen = round(time.time() * 1000)
        self.setPassword(data['password'])
        self.generateToken(data)
        info = {}
        info['user'] = self.getInfo(Type.PRIVATE)
        info['user']['token'] = self.token
        info['status'] = 1
        info['message'] = 'Registered'
        return info

    def preDelete(self):
        if not self.deleted:
            self.last_seen = round(time.time() * 1000)
            self.deleted = True
            self.save()

    def recover(self):
        self.deleted = False
        self.save()

    def fillFridge(self, products):
        response = {}
        fridge = self.fridge.split()
        try:
            for i in products:
                item = Ingredient.objects.get(id=int(i))
                fridge.append(str(item.id))
            self.fridge = " ".join(fridge)
            self.last_seen = round(time.time() * 1000)
            self.save()
            response = {"message": "Products added", "status": 1}
        except:
            response = {"message": "Wrong product id", "status": -1}
        response['user'] = {}
        return response

    def deleteFromFridge(self, products):
        response = {}
        fridge = self.fridge.split()
        try:
            for i in products:
                item = Ingredient.objects.get(id=int(i))
                if str(item.id) in fridge:
                    del fridge[fridge.index(str(item.id))]
            self.fridge = " ".join(fridge)
            self.last_seen = round(time.time() * 1000)
            self.save()
            response = {"message": "Products deleted", "status": 1}
        except:
            response = {"message": "Wrong product id", "status": -1}
        response['user'] = {}
        return response

    def unblockIngredient(self, i):
        response = {}
        banned = self.bannedIngredients.split()
        try:
            item = Ingredient.objects.get(id=int(i))
            if str(item.id) in banned:
                del banned[banned.index(str(item.id))]
            self.bannedIngredients = " ".join(banned)
            self.last_seen = round(time.time() * 1000)
            self.save()
            response = {"message": "Product unblocked", "status": 1}
        except:
            response = {"message": "Wrong product id", "status": -1}
        response['user'] = {}
        return response

    def banIngredient(self, i):
        response = {}
        banned = self.bannedIngredients.split()
        try:
            item = Ingredient.objects.get(id=int(i))
            if str(item.id) not in banned:
                banned.append(str(item.id))
            self.bannedIngredients = " ".join(banned)
            self.last_seen = round(time.time() * 1000)
            self.save()
            response = {"message": "Product banned", "status": 1}
        except:
            response = {"message": "Wrong product id", "status": -1}
        response['user'] = {}
        return response

    def banRecipe(self, recipeId):
        banned = self.bannedRecipes.split()
        try:
            item = Recipe.objects.get(id=int(recipeId))
            if str(item.id) not in banned:
                banned.append(str(item.id))
            self.bannedRecipes = " ".join(banned)
            self.last_seen = round(time.time() * 1000)
            self.save()
            response = {"message": "Recipe banned", "status": 1}
        except:
            response = {"message": "Wrong recipe id", "status": -1}
        response['user'] = {}
        return response

    def unblockRecipe(self, recipeId):
        banned = self.bannedRecipes.split()
        try:
            item = Recipe.objects.get(id=int(recipeId))
            if str(item.id) in banned:
                del banned[banned.index(str(item.id))]
            self.bannedRecipes = " ".join(banned)
            self.last_seen = round(time.time() * 1000)
            self.save()
            response = {"message": "Recipe unblocked", "status": 1}
        except:
            response = {"message": "Wrong recipe id", "status": -1}
        response['user'] = {}
        return response

    def unstarIngredient(self, products):
        response = {}
        starred = self.starredIngredients.split()
        try:
            for i in products:
                item = Ingredient.objects.get(id=int(i))
                if str(item.id) in starred:
                    del starred[starred.index(str(item.id))]
            self.starredIngredients = " ".join(starred)
            self.last_seen = round(time.time() * 1000)
            self.save()
            response = {"message": "Products deleted from starred", "status": 1}
        except:
            response = {"message": "Wrong product id", "status": -1}
        response['user'] = {}
        return response

    def starIngredient(self, i):
        starred = self.starredIngredients.split()
        try:
            item = Ingredient.objects.get(id=int(i))
            print(str(item.id))
            if str(item.id) not in starred:
                print("sad")
                starred.append(str(item.id))
            self.starredIngredients = " ".join(starred)
            self.last_seen = round(time.time() * 1000)
            self.save()
            response = {"message": "Product starred", "status": 1}
        except:
            response = {"message": "Wrong product id", "status": -1}
        response['user'] = {}
        return response

    def starRecipe(self, recipeId):
        starred = self.starredRecipes.split()
        try:
            item = Recipe.objects.get(id=int(recipeId))
            item.likeRecipe()
            if str(item.id) not in starred:
                starred.append(str(item.id))
            self.bannedRecipes = " ".join(starred)
            self.last_seen = round(time.time() * 1000)
            self.save()
            response = {"message": "Recipe starred", "status": 1}
        except:
            response = {"message": "Wrong recipe id", "status": -1}
        response['user'] = {}
        return response

    def unstarRecipe(self, recipeId):
        starred = self.starredRecipes.split()
        try:
            item = Recipe.objects.get(id=int(recipeId))
            item.dislikeRecipe()
            if str(item.id) in starred:
                del starred[starred.index(str(item.id))]
            self.bannedRecipes = " ".join(starred)
            self.last_seen = round(time.time() * 1000)
            self.save()
            response = {"message": "Recipe unblocked", "status": 1}
        except:
            response = {"message": "Wrong recipe id", "status": -1}
        response['user'] = {}
        return response


class Recipe(models.Model, Type):
    title = CharField(max_length=100)
    category = ForeignKey('RecipeCategory', on_delete=models.PROTECT)
    steps = TextField()
    ingredients = TextField()
    time = IntegerField()
    image = ImageField(upload_to=f'{STATICFILES_DIRS}/images', default=None)

    calories = IntegerField(default=None)
    proteins = IntegerField(default=None)
    carbs = IntegerField(default=None)
    fats = IntegerField(default=None)

    likes = IntegerField(default=0)
    comments = TextField(default='')
    userId = ForeignKey('User', on_delete=models.PROTECT, default=None)
    deleted = BooleanField(default=False)
    private = BooleanField(default=False)

    def getInfo(self) -> dict:
        dict = {}
        dict['title'] = self.title
        dict['category'] = self.category
        dict['steps'] = self.steps
        dict['ingredients'] = self.ingredients
        dict['time'] = self.time
        dict['image'] = self.image.name
        dict['calories'] = self.calories
        dict['proteins'] = self.proteins
        dict['carbs'] = self.carbs
        dict['fats'] = self.fats
        dict['likes'] = self.likes
        dict['comments'] = self.comments
        dict['userId'] = self.userId
        dict['deleted'] = self.deleted
        return dict

    def validateData(self, data):
        fields = ['title',
                  'steps',
                  'ingredients',
                  'time',
                  'category',
                  'token'
                  ]
        for i in data:
            del fields[fields.index(i)]
        if fields:
            raise MissFields(fields)

    def create(self, data):
        try:
            self.validateData(data)
            self.title = data['title']
            self.steps = data['steps']
            self.ingredients = data['ingredients']
            self.time = data['time']
            self.category = data['category']
            user = User.objects.get(token=data['token'])
            self.userId = user.id
            if 'calories' in data:
                self.calories = data['calories']
            if 'fats' in data:
                self.fats = data['fats']
            if 'carbs' in data:
                self.carbs = data['carbs']
            if 'proteins' in data:
                self.proteins = data['proteins']
            self.save()
            return {'message': 'Recipe created', 'recipe': self.getInfo(), 'status': -1}
        except MissFields as e:
            return {'message': str(e), 'recipe': {}, 'status': -1}
        except Exception as e:
            return {'message': str(e), 'status': -1, 'recipe': {}}

    def preDelete(self):
        self.deleted = True
        self.save()

    def setImage(self, image: UploadedFile):
        self.image = image
        self.save()

    def addComment(self, text, user):
        comment = TextMessage()
        comment.time = datetime.datetime.now()
        comment.userId = user
        comment.text = text

        comment.save()

        self.comments = self.comments + " " + comment.id
        self.save()

    def likeRecipe(self):
        self.likes += 1
        self.save()

    def dislikeRecipe(self):
        self.likes -= 1
        self.save()

    def editRecipe(self, data):
        fields = ['title',
                  'steps',
                  'ingredients',
                  'time',
                  'category',
                  ]

        for i in data:
            if i in fields:
                if i == 'title':
                    self.title = data[i]
                elif i == 'steps':
                    self.steps = data[i]
                elif i == 'ingredients':
                    self.ingredients = data[i]
                elif i == 'time':
                    self.time = data[i]
                elif i == 'category':
                    self.category = data[i]
        self.save()


class RecipeCategory(models.Model, Type):
    title = TextField()


class Chat(models.Model, Type):
    members = TextField()
    attachments = TextField()
    messages = TextField()

    def addAttachment(self, id):
        if self.attachments != "" or self.attachments is not None:
            self.attachments = self.attachments + " " + id
        else:
            self.attachments = id
        self.save()

    def addMessage(self, id: int):
        if self.messages != "" or self.messages is not None:
            self.messages = " " + str(id)
        else:
            self.messages = str(id)
        self.save()


class Forum(models.Model, Type):
    title = TextField()
    owner = ForeignKey('User', on_delete=models.PROTECT)
    members = TextField()
    messages = TextField()
    deleted = BooleanField(default=False)

    def addMember(self, id: int):
        try:
            user = User.objects.get(id=id)
            usr_forums = user.forums.split()
            if str(id) not in usr_forums:
                memebers = self.members.split()
                memebers.append(str(id))
                self.members = " ".join(memebers)
                del usr_forums[usr_forums.index(str(id))]
                response = {"message": f"User id={id} added to topic", "status": 1}
            else:
                response = {"message": f"User id={id} added to topic", "status": 1}
        except:
            response = {"message": f"User id={id} not topic", "status": -1}

        self.save()

    def deleteMember(self, id: int):
        try:
            user = User.objects.get(id=id)
            usr_forums = user.forums.split()
            if str(id) in usr_forums:
                members = self.members.split()
                del members[members.index(str(id))]
                self.members = " ".join(members)
                del usr_forums[usr_forums.index(str(id))]
                response = {"message": f"User id={id} deleted to topic", "status": 1}
            else:
                response = {"message": f"User id={id} deleted to topic", "status": 1}
        except:
            response = {"message": f"User id={id} not topic", "status": -1}
        self.save()
        return response

    def addMessage(self, id: int):
        try:
            msg = self.messages.split()
            message = TextMessage.objects.get(id=id)
            msg.append(str(message.id))
            self.messages = " ".join(msg)
            response = {"message": f"Message added", "status": 1,}
        except Exception as e:
            response = {"message": f"Message id={id} not topic", "status": -1, "exception": str(e)}
        self.save()
        return response

    def preDelete(self):
        self.deleted = True
        self.save()


class Ingredient(models.Model, Type):
    title = TextField()
    category = ForeignKey('IngredientCategory', on_delete=models.PROTECT)


class IngredientCategory(models.Model, Type):
    title = TextField()


class Attachments(models.Model, Type):
    time = DateTimeField()
    file = FileField()


class TextMessage(models.Model, Type):
    time = DateTimeField()
    text = TextField()
    userId = ForeignKey('User', on_delete=models.PROTECT)
