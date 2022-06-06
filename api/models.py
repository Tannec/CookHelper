import time
import jwt
from django.core.files.uploadedfile import UploadedFile
from django.db import models
from django.db.models import *
from werkzeug.security import *
import datetime
from cookhelper.settings import SECRET_KEY, STATICFILES_DIRS, MEDIA_ROOT


# models: Recipe, User, Forum, Ingredient, Dialog


class Type:
    PRIVATE = 1
    GENERAL = 0


class UnknownField(Exception):

    def __init__(self, field):
        super().__init__()
        self.field = field

    def __str__(self):
        return 'Wrong field detected'

    def unknownField(self):
        return self.field


class MissFields(Exception):
    def __init__(self, elems):
        super().__init__()
        self.fields = elems

    def __str__(self):
        return 'Missed some fields'

    def missedFields(self):
        return ", ".join(self.fields)


class User(models.Model, Type):
    name = CharField(max_length=40)
    surname = CharField(max_length=40)
    email = EmailField(max_length=100, unique=True)
    avatar = ImageField(upload_to=f'{MEDIA_ROOT}')
    nickname = CharField(max_length=100, default="")

    login = CharField(max_length=100, unique=True)
    password = TextField()
    token = CharField(max_length=512)
    deleted = BooleanField(default=False)

    fridge = TextField(default="")
    forums = TextField(default="")
    starredRecipes = TextField(default="")
    bannedRecipes = TextField(default="")
    starredIngredients = TextField(default="")
    bannedIngredients = TextField(default="")
    ownRecipes = TextField(default="")

    def setPassword(self, password):
        self.password = generate_password_hash(password)
        self.save()

    def validatePassword(self, password):
        return check_password_hash(self.password, password)

    def generateToken(self, data: dict):
        data['time'] = round(time.time() * 1000)
        data['prohodnoyeSlovoComrad'] = self.password
        tt = jwt.encode(data, SECRET_KEY, algorithm='HS256')
        self.token = tt
        self.save()

    def validateToken(self, token: str):
        return self.token == token

    def setAvatar(self, image: UploadedFile):
        self.avatar = image
        self.save()

    def validateData(self, data):
        fields = ['name',
                  'surname',
                  'email',
                  'login',
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

    def getInfo(self, type) -> dict:
        try:
            dict = {}
            dict['status'] = 1
            dict['name'] = self.name
            dict['nickaname'] = self.nickname
            dict['email'] = self.email
            dict['surname'] = self.surname
            dict['avatar'] = self.avatar.name
            if type == self.PRIVATE:
                dict['login'] = self.login
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

    def auth(self, login=None, password=None):
        if login == self.login and self.validatePassword(password):
            return {'token': self.token, 'status': 1}
        else:
            return {'message': 'Wrong credentials', 'status': -1}

    def register(self, data):
        try:
            self.validateData(data)
            self.name = data['name']
            self.nickname = data['nickname']
            self.surname = data['surname']
            self.email = data['email']
            self.login = data['login']
            self.setPassword(data['password'])
            self.generateToken(data)
            info = {}
            info['user'] = self.getInfo(1)
            info['user']['token'] = self.token
            info['status'] = 1
            info['message'] = 'Registered'
            return info
        except UnknownField as e:
            return {'message': str(e), 'field': e.unknownField(), 'status': -1}
        except MissFields as e:
            return {'message': str(e), 'fields': e.missedFields(), 'status': -1}
        except Exception as e:
            return {'message': str(e), 'status': -1}

    def preDelete(self):
        if not self.deleted:
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
            self.save()
            response = {"message": "Products added", "status": 1}
        except:
            response = {"message": "Wrong product id", "status": -1}
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
            self.save()
            response = {"message": "Products deleted", "status": 1}
        except:
            response = {"message": "Wrong product id", "status": -1}
        return response

    def unblockIngredient(self, i):
        response = {}
        banned = self.bannedIngredients.split()
        try:
            item = Ingredient.objects.get(id=int(i))
            if str(item.id) in banned:
                del banned[banned.index(str(item.id))]
            self.bannedIngredients = " ".join(banned)
            self.save()
            response = {"message": "Product unblocked", "status": 1}
        except:
            response = {"message": "Wrong product id", "status": -1}
        return response

    def banIngredient(self, i):
        response = {}
        banned = self.bannedIngredients.split()
        try:
            item = Ingredient.objects.get(id=int(i))
            if str(item.id) not in banned:
                banned.append(str(item.id))
            self.bannedIngredients = " ".join(banned)
            self.save()
            response = {"message": "Product banned", "status": 1}
        except:
            response = {"message": "Wrong product id", "status": -1}
        return response

    def banRecipe(self, recipeId):
        banned = self.bannedRecipes.split()
        try:
            item = Recipe.objects.get(id=int(recipeId))
            if str(item.id) not in banned:
                banned.append(str(item.id))
            self.bannedRecipes = " ".join(banned)
            self.save()
            response = {"message": "Recipe banned", "status": 1}
        except:
            response = {"message": "Wrong recipe id", "status": -1}
        return response

    def unblockRecipe(self, recipeId):
        banned = self.bannedRecipes.split()
        try:
            item = Recipe.objects.get(id=int(recipeId))
            if str(item.id) in banned:
                del banned[banned.index(str(item.id))]
            self.bannedRecipes = " ".join(banned)
            self.save()
            response = {"message": "Recipe unblocked", "status": 1}
        except:
            response = {"message": "Wrong recipe id", "status": -1}
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
            self.save()
            response = {"message": "Products deleted from starred", "status": 1}
        except:
            response = {"message": "Wrong product id", "status": -1}
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
            self.save()
            response = {"message": "Product starred", "status": 1}
        except:
            response = {"message": "Wrong product id", "status": -1}
        return response

    def starRecipe(self, recipeId):
        starred = self.starredRecipes.split()
        try:
            item = Recipe.objects.get(id=int(recipeId))
            item.likeRecipe()
            if str(item.id) not in starred:
                starred.append(str(item.id))
            self.bannedRecipes = " ".join(starred)
            self.save()
            response = {"message": "Recipe starred", "status": 1}
        except:
            response = {"message": "Wrong recipe id", "status": -1}
        return response

    def unstarRecipe(self, recipeId):
        starred = self.starredRecipes.split()
        try:
            item = Recipe.objects.get(id=int(recipeId))
            item.dislikeRecipe()
            if str(item.id) in starred:
                del starred[starred.index(str(item.id))]
            self.bannedRecipes = " ".join(starred)
            self.save()
            response = {"message": "Recipe unblocked", "status": 1}
        except:
            response = {"message": "Wrong recipe id", "status": -1}
        return response


class Recipe(models.Model, Type):
    title = CharField(max_length=100)
    category = ForeignKey('RecipeCategory', on_delete=models.PROTECT)
    steps = TextField()
    ingredients = TextField()
    time = IntegerField()
    image = ImageField(upload_to=f'{STATICFILES_DIRS}/images', default=None)

    calories = IntegerField()
    proteins = IntegerField(default=None)
    carbs = IntegerField(default=None)
    fats = IntegerField(default=None)

    likes = IntegerField(default=0)
    comments = TextField(default='')
    userId = ForeignKey('User', on_delete=models.PROTECT, default=None)
    deleted = BooleanField(default=False)

    def getInfo(self):
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
                  'userId'
                  ]
        for i in data:
            if i not in fields:
                raise UnknownField(i)
                return
            else:
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
            self.userId = data['userId']
        except UnknownField as e:
            try:
                self.calories = data['calories']
                self.fats = data['fats']
                self.carbs = data['carbs']
                self.proteins = data['proteins']
            except:
                pass
        except MissFields as e:
            return {'message': str(e), 'fields': e.missedFields(), 'status': -1}
        except Exception as e:
            return {'message': str(e), 'status': -1}

    def preDelete(self):
        self.deleted = True

    def setImage(self, image: UploadedFile):
        self.image = image

    def addComment(self, text, user):
        comment = TextMessages()
        comment.time = datetime.datetime.now()
        comment.userId = user
        comment.text = text

        comment.save()

        self.comments = self.comments + " " + comment.id

    def likeRecipe(self):
        self.likes += 1

    def dislikeRecipe(self):
        self.likes -= 1

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

    def addMessage(self, id: int):
        if self.messages != "" or self.messages is not None:
            self.messages = " " + str(id)
        else:
            self.messages = str(id)


class Forum(models.Model, Type):
    title = TextField()
    owner = ForeignKey('User', on_delete=models.PROTECT)
    members = TextField()
    messages = TextField()

    def addMember(self, id: int):
        self.members = " " + str(id)

    def deleteMember(self, id: int):
        self.members = "".join(self.members.split(" " + str(id)))

    def addMessage(self, id: int):
        if self.messages != "" or self.messages is not None:
            self.messages = " " + str(id)
        else:
            self.messages = str(id)


class Ingredient(models.Model, Type):
    title = TextField()
    category = ForeignKey('IngredientCategory', on_delete=models.PROTECT)


class IngredientCategory(models.Model, Type):
    title = TextField()


class Attachments(models.Model, Type):
    time = DateTimeField()
    file = FileField()


class TextMessages(models.Model, Type):
    time = DateTimeField()
    text = TextField()
    userId = ForeignKey('User', on_delete=models.PROTECT)
