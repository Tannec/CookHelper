import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics

from api.models import User


def authorize(request):
    login = request.GET.get('login', None)
    password = request.GET.get('password', None)
    if login is None:
        return JsonResponse({'message': 'Missed login', 'status': -1})
    if password is None:
        return JsonResponse({'message': 'Missed password', 'status': -1})
    user = None
    try:
        user = User.objects.get(login=login)
    except:
        pass
    if user is None:
        return JsonResponse({'message': f"User with login '{login}' not found", 'status': -1})
    if user.validatePassword(password):
        response = user.getInfo(1)
        response['token'] = user.token
        return JsonResponse({'message': 'Authorized', 'user': response, 'status': 1})
    else:
        return JsonResponse({"message": "Wrong credentials", "status": -1})


def changePassword(request):
    token = request.GET.get('token', None)
    old_password = request.GET.get('old_password', None)
    new_password = request.GET.get('new_password', None)
    if token is None:
        return JsonResponse({'message': 'Missed token', 'status': -1})
    if old_password is None:
        return JsonResponse({'message': 'Missed old password', 'status': -1})
    if new_password is None:
        return JsonResponse({'message': 'Missed new password', 'status': -1})
    try:
        user = User.objects.get(token=token)
    except:
        return JsonResponse({'message': f"Wrong token", 'status': -1})
    if user.validatePassword(old_password):
        user.generateToken(user.getInfo(1))
        user.setPassword(new_password)
        return JsonResponse({'message': 'Password changed', 'token': user.token, 'status': 1})
    else:
        return JsonResponse({"message": "Wrong old password", "status": -1})


def register(request):
    user = User()
    response = user.register(request.GET.dict())
    if response['status'] == 1:
        user.save()
    return JsonResponse(response)


def info(request):
    response = {}
    id = request.GET.get('id', None)
    field = request.GET.get('field', None)
    token = request.GET.get('token', None)
    if id is None:
        if token is None:
            response = {"message": "TOKEN or ID required", "status": -1}
        else:
            try:
                user = User.objects.get(token=token)
                if user.deleted:
                    return JsonResponse({"message": "User deleted", "status": 1})
                response['user'] = user.getInfo(1)
                response['status'] = 1
            except Exception as e:
                response = {"message": "Wrong token", "exception": str(e), "status": -1}
    else:
        try:
            user_requested = User.objects.get(id=id)
            if user_requested.deleted:
                return JsonResponse({"message": "User deleted", "status": 1})
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
                    response = {"message": "Permission denied", "status": -1}
        except Exception as e:
            response = {"message": f"User with id={id} not found", "exception": str(e), "status": -1}
    return JsonResponse(response)


def delete(request):
    password = request.GET.get('password', None)
    token = request.GET.get('token', None)
    if token is None:
        response = {"message": "Wrong token", "status": -1}
        return JsonResponse(response)
    if password is None:
        response = {"message": "Wrong password", "status": -1}
        return JsonResponse(response)

    try:
        user = User.objects.get(token=token)
        if user.validatePassword(password):
            user.preDelete()
            response = {"message": "User deleted", "status": 1}
        else:
            response = {"message": "Wrong password", "status": -1}
    except Exception as e:
        response = {"message": "Wrong token", "exception": str(e), "status": -1}
    return JsonResponse(response)


def recover(request):
    password = request.GET.get('password', None)
    login = request.GET.get('login', None)
    if login is None:
        response = {"message": "Wrong login", "status": -1}
        return JsonResponse(response)
    if password is None:
        response = {"message": "Wrong password", "status": -1}
        return JsonResponse(response)
    try:
        user = User.objects.get(login=login)
        if user.validatePassword(password):
            user.recover()
            response = {"message": "User recovered", "status": 1}
        else:
            response = {"message": "Wrong password", "status": -1}
    except Exception as e:
        response = {"message": f"User with login '{login}' not found", "exception": str(e), "status": -1}
    return JsonResponse(response)


@csrf_exempt
def setAvatar(request):
    image = request.FILES['image']
    token = request.GET.get('token', None)
    if token is None:
        response = {"message": "Wrong token", "status": -1}
    else:
        try:
            user = User.objects.get(token=token)
            user.setAvatar(image)
            response = {"message": "Avatar uploaded", "status": 1}
        except Exception as e:
            response = {"message": "Wrong params", "exception": str(e), "status": -1}
    return JsonResponse(response)


def fillFridge(request):
    products = request.GET.get('products', None)
    token = request.GET.get('token', None)
    if token is None:
        response = {"message": "Wrong token", "status": -1}
    else:
        try:
            user = User.objects.get(token=token)
            if products is None:
                response = {"message": "At least 1 product required", "status": -1}
            else:
                response = user.fillFridge(products)
        except Exception as e:
            response = {"message": "Wrong token", "exception": str(e), "status": -1}
    return JsonResponse(response)


def deleteFromFridge(request):
    products = request.GET.get('products', None)
    token = request.GET.get('token', None)
    if token is None:
        response = {"message": "Wrong token", "status": -1}
    else:
        try:
            user = User.objects.get(token=token)
            if products is None:
                response = {"message": "At least 1 product required", "status": -1}
            else:
                response = user.deleteFromFridge(products)
        except Exception as e:
            response = {"message": "Wrong token", "exception": str(e), "status": -1}
    return JsonResponse(response)


def banIngredient(request):
    product = request.GET.get('product', None)
    token = request.GET.get('token', None)
    if token is None:
        response = {"message": "Wrong token", "status": -1}
    else:
        try:
            user = User.objects.get(token=token)
            if product is None:
                response = {"message": "Product required", "status": -1}
            else:
                response = user.banIngredient(product)
        except Exception as e:
            response = {"message": "Wrong token", "exception": str(e), "status": -1}
    return JsonResponse(response)


def unblockIngredient(request):
    product = request.GET.get('product', None)
    token = request.GET.get('token', None)
    if token is None:
        response = {"message": "Wrong token", "status": -1}
    else:
        try:
            user = User.objects.get(token=token)
            if product is None:
                response = {"message": "Product required", "status": -1}
            else:
                response = user.unblockIngredient(product)
        except Exception as e:
            response = {"message": "Wrong token", "exception": str(e), "status": -1}
    return JsonResponse(response)


def banRecipe(request):
    recipe = request.GET.get('recipe', None)
    token = request.GET.get('token', None)
    if token is None:
        response = {"message": "Wrong token", "status": -1}
    else:
        try:
            user = User.objects.get(token=token)
            if recipe is None:
                response = {"message": "Recipe required", "status": -1}
            else:
                response = user.banRecipe(recipe)
        except Exception as e:
            response = {"message": "Wrong token", "exception": str(e), "status": -1}
    return JsonResponse(response)


def unblockRecipe(request):
    recipe = request.GET.get('recipe', None)
    token = request.GET.get('token', None)
    if token is None:
        response = {"message": "Wrong token", "status": -1}
    else:
        try:
            user = User.objects.get(token=token)
            if recipe is None:
                response = {"message": "Recipe required", "status": -1}
            else:
                response = user.unblockRecipe(recipe)
        except Exception as e:
            response = {"message": "Wrong token", "exception": str(e), "status": -1}
    return JsonResponse(response)


def starIngredient(request):
    product = request.GET.get('product', None)
    token = request.GET.get('token', None)
    if token is None:
        response = {"message": "Wrong token", "status": -1}
    else:
        try:
            user = User.objects.get(token=token)
            if product is None:
                response = {"message": "Product required", "status": -1}
            else:
                response = user.starIngredient(product)
        except Exception as e:
            response = {"message": "Wrong token", "exception": str(e), "status": -1}
    return JsonResponse(response)


def unstarIngredient(request):
    product = request.GET.get('product', None)
    token = request.GET.get('token', None)
    if token is None:
        response = {"message": "Wrong token", "status": -1}
    else:
        try:
            user = User.objects.get(token=token)
            if product is None:
                response = {"message": "Product required", "status": -1}
            else:
                response = user.unstarIngredient(product)
        except Exception as e:
            response = {"message": "Wrong token", "exception": str(e), "status": -1}
    return JsonResponse(response)


def starRecipe(request):
    recipe = request.GET.get('recipe', None)
    token = request.GET.get('token', None)
    if token is None:
        response = {"message": "Wrong token", "status": -1}
    else:
        try:
            user = User.objects.get(token=token)
            if recipe is None:
                response = {"message": "Recipe required", "status": -1}
            else:
                response = user.starRecipe(recipe)
        except Exception as e:
            response = {"message": "Wrong token", "exception": str(e), "status": -1}
    return JsonResponse(response)


def unstarRecipe(request):
    recipe = request.GET.get('recipe', None)
    token = request.GET.get('token', None)
    if token is None:
        response = {"message": "Wrong token", "status": -1}
    else:
        try:
            user = User.objects.get(token=token)
            if recipe is None:
                response = {"message": "Recipe required", "status": -1}
            else:
                response = user.unstarRecipe(recipe)
        except Exception as e:
            response = {"message": "Wrong token", "exception": str(e), "status": -1}
    return JsonResponse(response)