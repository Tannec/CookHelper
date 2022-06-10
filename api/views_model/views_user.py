import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics
from api.post_service.service import sendVerificationMail


from api.models import User

def sendMail(request):
    state = sendVerificationMail(code="123456", email='artur.231456@gmail.com')
    return JsonResponse({'message': 'qweqwe', 'status': 1, 'user': f'{state}'})


def authorize(request):
    nickname = request.GET.get('nickname', None)
    email = request.GET.get('email', None)
    password = request.GET.get('password', None)
    if nickname is None and email is None:
        return JsonResponse({'message': 'Missed login like nickname or email', 'status': -1, 'user': {}})
    if password is None:
        return JsonResponse({'message': 'Missed password', 'status': -1, 'user': {}})
    user = None
    try:
        if nickname is not None:
            user = User.objects.get(nickname=nickname)
        else:
            user = User.objects.get(email=email)
        if not user.verified:
            code = user.generateCode()
            state = sendVerificationMail(code=code, email=user.email)
            return JsonResponse({'message': 'User not verified', 'status': -1, 'user': user.getInfo(0)})
    except:
        pass
    if user is None:
        return JsonResponse({'message': f"User with login data nickname={nickname} or email={email} not found", 'status': -1, 'user': {
            }})
    if user.validatePassword(password):
        response = user.getInfo(1)
        response['token'] = user.token
        return JsonResponse({'message': 'Authorized', 'user': response, 'status': 1})
    else:
        return JsonResponse({"message": "Wrong credentials", "status": -1, 'user': {}})


def changePassword(request):
    token = request.GET.get('token', None)
    old_password = request.GET.get('old_password', None)
    new_password = request.GET.get('new_password', None)
    if token is None:
        return JsonResponse({'message': 'Missed token', 'status': -1, 'user': {}})
    if old_password is None:
        return JsonResponse({'message': 'Missed old password', 'status': -1, 'user': {}})
    if new_password is None:
        return JsonResponse({'message': 'Missed new password', 'status': -1, 'user': {}})
    try:
        user = User.objects.get(token=token)
    except:
        return JsonResponse({'message': f"Wrong token", 'status': -1, 'user': {}})
    if user.validatePassword(old_password):
        user.generateToken(user.getInfo(1))
        user.setPassword(new_password)
        return JsonResponse({'message': 'Password changed', 'token': user.token, 'status': 1, 'user': {}})
    else:
        return JsonResponse({"message": "Wrong old password", "status": -1, 'user': {}})


@csrf_exempt
def register(request):
    user = User()
    response = user.register(request.GET.dict())
    if response['status'] == 1:
        user.save()
        code = user.generateCode(6)
        state = sendVerificationMail(code=code, email=user.email)
    return JsonResponse(response)


def info(request):
    response = {}
    id = request.GET.get('id', None)
    field = request.GET.get('field', None)
    token = request.GET.get('token', None)
    if id is None:
        if token is None:
            response = {"message": "TOKEN or ID required", "status": -1, 'user': {}}
        else:
            try:
                user = User.objects.get(token=token)
                if user.deleted:
                    return JsonResponse({"message": "User deleted", "status": -1, 'user': {}})
                response['user'] = user.getInfo(1)
                response['status'] = 1
            except Exception as e:
                response = {"message": "Wrong token", "exception": str(e), "status": -1, 'user': {}}
    else:
        try:
            user_requested = User.objects.get(id=id)
            if user_requested.deleted:
                return JsonResponse({"message": "User deleted", "status": 1, 'user': {}})
            type = 1 if user_requested.token == token else 0
            if field is None:
                response['user'] = user_requested.getInfo(type)
                response['status'] = 1
            else:
                info = user_requested.getInfo(type)
                if field in info:
                    response['user'] = {field: info[field]}
                    response['status'] = 1
                else:
                    response = {"message": "Permission denied", "status": -1, 'user': {}}
        except Exception as e:
            response = {"message": f"User with id={id} not found", "exception": str(e), "status": -1, 'user': {}}
    return JsonResponse(response)


def delete(request):
    password = request.GET.get('password', None)
    token = request.GET.get('token', None)
    if token is None:
        response = {"message": "Wrong token", "status": -1, 'user': {}}
        return JsonResponse(response)
    if password is None:
        response = {"message": "Wrong password", "status": -1, 'user': {}}
        return JsonResponse(response)

    try:
        user = User.objects.get(token=token)
        if user.validatePassword(password):
            user.preDelete()
            response = {"message": "User deleted", "status": 1, 'user': {}}
        else:
            response = {"message": "Wrong password", "status": -1, 'user': {}}
    except Exception as e:
        response = {"message": "Wrong token", "exception": str(e), "status": -1, 'user': {}}
    return JsonResponse(response)


def recover(request):
    password = request.GET.get('password', None)
    login = request.GET.get('login', None)
    if login is None:
        response = {"message": "Wrong login", "status": -1, 'user': {}}
        return JsonResponse(response)
    if password is None:
        response = {"message": "Wrong password", "status": -1, 'user': {}}
        return JsonResponse(response)
    try:
        user = User.objects.get(login=login)
        if user.validatePassword(password):
            user.recover()
            response = {"message": "User recovered", "status": 1, 'user': {}}
        else:
            response = {"message": "Wrong password", "status": -1, 'user': {}}
    except Exception as e:
        response = {"message": f"User with login '{login}' not found", "exception": str(e), "status": -1}
    return JsonResponse(response)


@csrf_exempt
def setAvatar(request):
    image = request.FILES['image']
    token = request.GET.get('token', None)
    if token is None:
        response = {"message": "Wrong token", "status": -1, 'user': {}}
    else:
        try:
            user = User.objects.get(token=token)
            user.setAvatar(image)
            response = {"message": "Avatar uploaded", "status": 1, 'user': {}}
        except Exception as e:
            response = {"message": "Wrong params", "exception": str(e), "status": -1, 'user': {}}
    return JsonResponse(response)


def fillFridge(request):
    products = request.GET.get('products', None)
    token = request.GET.get('token', None)
    if token is None:
        response = {"message": "Wrong token", "status": -1, 'user': {}}
    else:
        try:
            user = User.objects.get(token=token)
            if products is None:
                response = {"message": "At least 1 product required", "status": -1, 'user': {}}
            else:
                response = user.fillFridge(products)
        except Exception as e:
            response = {"message": "Wrong token", "exception": str(e), "status": -1, 'user': {}}
    return JsonResponse(response)


def deleteFromFridge(request):
    products = request.GET.get('products', None)
    token = request.GET.get('token', None)
    if token is None:
        response = {"message": "Wrong token", "status": -1, 'user': {}}
    else:
        try:
            user = User.objects.get(token=token)
            if products is None:
                response = {"message": "At least 1 product required", "status": -1, 'user': {}}
            else:
                response = user.deleteFromFridge(products)
        except Exception as e:
            response = {"message": "Wrong token", "exception": str(e), "status": -1, 'user': {}}
    return JsonResponse(response)


def banIngredient(request):
    product = request.GET.get('product', None)
    token = request.GET.get('token', None)
    if token is None:
        response = {"message": "Wrong token", "status": -1, 'user': {}}
    else:
        try:
            user = User.objects.get(token=token)
            if product is None:
                response = {"message": "Product required", "status": -1, 'user': {}}
            else:
                response = user.banIngredient(product)
        except Exception as e:
            response = {"message": "Wrong token", "exception": str(e), "status": -1, 'user': {}}
    return JsonResponse(response)


def unblockIngredient(request):
    product = request.GET.get('product', None)
    token = request.GET.get('token', None)
    if token is None:
        response = {"message": "Wrong token", "status": -1, 'user': {}}
    else:
        try:
            user = User.objects.get(token=token)
            if product is None:
                response = {"message": "Product required", "status": -1, 'user': {}}
            else:
                response = user.unblockIngredient(product)
        except Exception as e:
            response = {"message": "Wrong token", "exception": str(e), "status": -1, 'user': {}}
    return JsonResponse(response)


def banRecipe(request):
    recipe = request.GET.get('recipe', None)
    token = request.GET.get('token', None)
    if token is None:
        response = {"message": "Wrong token", "status": -1, 'user': {}}
    else:
        try:
            user = User.objects.get(token=token)
            if recipe is None:
                response = {"message": "Recipe required", "status": -1, 'user': {}}
            else:
                response = user.banRecipe(recipe)
        except Exception as e:
            response = {"message": "Wrong token", "exception": str(e), "status": -1, 'user': {}}
    return JsonResponse(response)


def unblockRecipe(request):
    recipe = request.GET.get('recipe', None)
    token = request.GET.get('token', None)
    if token is None:
        response = {"message": "Wrong token", "status": -1, 'user': {}}
    else:
        try:
            user = User.objects.get(token=token)
            if recipe is None:
                response = {"message": "Recipe required", "status": -1, 'user': {}}
            else:
                response = user.unblockRecipe(recipe)
        except Exception as e:
            response = {"message": "Wrong token", "exception": str(e), "status": -1, 'user': {}}
    return JsonResponse(response)


def addForum(request):
    forum = request.GET.get('forum', None)
    token = request.GET.get('token', None)
    if token is None:
        response = {"message": "Wrong token", "status": -1, 'user': {}}
    else:
        try:
            user = User.objects.get(token=token)
            if forum is None:
                response = {"message": "Forum required", "status": -1, 'user': {}}
            else:
                response = user.addForum(forum)
        except Exception as e:
            response = {"message": "Wrong token", "exception": str(e), "status": -1, 'user': {}}
    return JsonResponse(response)


def deleteForum(request):
    forum = request.GET.get('forum', None)
    token = request.GET.get('token', None)
    if token is None:
        response = {"message": "Wrong token", "status": -1, 'user': {}}
    else:
        try:
            user = User.objects.get(token=token)
            if forum is None:
                response = {"message": "Forum required", "status": -1, 'user': {}}
            else:
                response = user.deleteForum(forum)
        except Exception as e:
            response = {"message": "Wrong token", "exception": str(e), "status": -1, 'user': {}}
    return JsonResponse(response)


def starIngredient(request):
    product = request.GET.get('product', None)
    token = request.GET.get('token', None)
    if token is None:
        response = {"message": "Wrong token", "status": -1, 'user': {}}
    else:
        try:
            user = User.objects.get(token=token)
            if product is None:
                response = {"message": "Product required", "status": -1, 'user': {}}
            else:
                response = user.starIngredient(product)
        except Exception as e:
            response = {"message": "Wrong token", "exception": str(e), "status": -1, 'user': {}}
    return JsonResponse(response)


def unstarIngredient(request):
    product = request.GET.get('product', None)
    token = request.GET.get('token', None)
    if token is None:
        response = {"message": "Wrong token", "status": -1, 'user': {}}
    else:
        try:
            user = User.objects.get(token=token)
            if product is None:
                response = {"message": "Product required", "status": -1, 'user': {}}
            else:
                response = user.unstarIngredient(product)
        except Exception as e:
            response = {"message": "Wrong token", "exception": str(e), "status": -1, 'user': {}}
    return JsonResponse(response)


def starRecipe(request):
    recipe = request.GET.get('recipe', None)
    token = request.GET.get('token', None)
    if token is None:
        response = {"message": "Wrong token", "status": -1, 'user': {}}
    else:
        try:
            user = User.objects.get(token=token)
            if recipe is None:
                response = {"message": "Recipe required", "status": -1, 'user': {}}
            else:
                response = user.starRecipe(recipe)
        except Exception as e:
            response = {"message": "Wrong token", "exception": str(e), "status": -1, 'user': {}}
    return JsonResponse(response)


def unstarRecipe(request):
    recipe = request.GET.get('recipe', None)
    token = request.GET.get('token', None)
    if token is None:
        response = {"message": "Wrong token", "status": -1, 'user': {}}
    else:
        try:
            user = User.objects.get(token=token)
            if recipe is None:
                response = {"message": "Recipe required", "status": -1, 'user': {}}
            else:
                response = user.unstarRecipe(recipe)
        except Exception as e:
            response = {"message": "Wrong token", "exception": str(e), "status": -1, 'user': {}}
    return JsonResponse(response)


def verifyUser(request):
    code = request.GET.get('code', None)
    token = request.GET.get('token', None)

    try:
        if token is None:
            raise Exception('Token required')
        if code is None:
            raise Exception('Code required')

        user = User.objects.get(token=token)

        if user.verifyCode(code):
            response = {'message': 'Account verified', 'status': 1}
        else:
            response = {'message': 'Wrong code', 'status': 1}
    except Exception as e:
        response = {'message': str(e), 'status': -1}
    response['user'] = {}
    return JsonResponse(response)