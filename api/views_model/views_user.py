import json
from django.db.models import Q
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics
from api.post_service.service import sendVerificationMail, sendRecoveryMail
from api.views_model.static_functions import *
from api.models import User, Type


@csrf_exempt
def authorize(request):
    login = clear(request.POST.get('login', None))
    password = clear(request.POST.get('password', None))

    userInfo = {}
    response = {}

    try:
        if login is None:
            raise FieldRequiredException('login')
        if password is None:
            raise FieldRequiredException('password')

        user = User.objects.get(Q(nickname=login) | Q(email=login))

        if user.validatePassword(password):
            userInfo = user.getInfo(1)
            userInfo['token'] = user.token
            if user.verified:
                raise SuccessException(message='Authorized')
            else:
                raise SuccessException(message='User not verified',
                                       status=103)
        else:
            raise ModelException(message='Wrong credentials',
                                 status=102)

    except SuccessException as e:
        status = int(e)
        message = str(e)
    except ModelException as e:
        status = int(e)
        message = str(e)
    except User.DoesNotExist as e:
        status = 101
        message = str(e)
    except PermissionException as e:
        message = str(e)
        status = int(e)
    except FieldRequiredException as e:
        message = str(e)
        status = int(e)
    except Exception as e:
        message = str(e)
        status = 199

    response['message'] = message
    response['status'] = status
    response['user'] = userInfo

    return JsonResponse(response)


@csrf_exempt
def changePassword(request):
    token = clear(request.POST.get('token', None))
    old_password = clear(request.POST.get('old_password', None))
    new_password = clear(request.POST.get('new_password', None))

    response = {}
    userInfo = {}
    message = 'Some exception'
    status = 199

    try:
        if token is None:
            raise FieldRequiredException('token')
        if old_password is None:
            raise FieldRequiredException('old password')
        if new_password is None:
            raise FieldRequiredException('new password')

        user = User.objects.get(token=token)

        if user.validatePassword(old_password):
            user.passwordAvailability(new_password)
            user.generateToken(user.getInfo(1))
            user.setPassword(new_password)
            userInfo = user.getInfo(Type.PRIVATE)
            raise SuccessException(message='Password changed')
        else:
            raise ModelException(status=102,
                                 message='Wrong password')

    except SuccessException as e:
        status = int(e)
        message = str(e)
    except ModelException as e:
        status = int(e)
        message = str(e)
    except User.DoesNotExist as e:
        status = 102
        message = str(e)
    except PermissionException as e:
        message = str(e)
        status = int(e)
    except FieldRequiredException as e:
        message = str(e)
        status = int(e)
    except Exception as e:
        message = str(e)
        status = 199

    response['message'] = message
    response['status'] = status
    response['user'] = userInfo

    return JsonResponse(response)


@csrf_exempt
def register(request):
    data = clear(request.POST.dict())

    userInfo = {}
    response = {}
    message = 'Exception'
    status = 199

    try:
        user = User()

        response = user.register(data)
        if 'avatar' in request.FILES:
            user.setAvatar(request.FILES['avatar'])
        user.save()

        code = user.generateCode(6)
        userInfo = user.getInfo(Type.PRIVATE)

        state = sendVerificationMail(code=code, email=user.email, name=user.name)
        if state is True:
            raise SuccessException(message='Registered')
        else:
            raise SuccessException(message='Code has not been sent')

    except SuccessException as e:
        status = int(e)
        message = str(e)
    except ModelException as e:
        status = int(e)
        message = str(e)
    except User.DoesNotExist as e:
        status = 101
        message = str(e)
    except PermissionException as e:
        message = str(e)
        status = int(e)
    except FieldRequiredException as e:
        message = str(e)
        status = int(e)
    except RejectException as e:
        message = str(e)
        status = int(e)
    except Exception as e:
        message = str(e)
        status = 199

    response['status'] = status
    response['message'] = message
    response['user'] = userInfo

    return JsonResponse(response)


def info(request):
    id = request.GET.get('id', None)
    field = request.GET.get('field', None)
    token = request.GET.get('token', None)

    response = {}
    message = {}
    userInfo = {}
    status = 199
    privacy = Type.PRIVATE

    try:
        if id is None:
            raise FieldRequiredException('User id required')
        if field is None:
            raise FieldRequiredException('User field required')
        if token is None:
            raise FieldRequiredException('User token required')

        user = User.objects.get(token=token)
        userRequired = User.objects.get(id=id)

        if user != userRequired:
            privacy = Type.GENERAL

        info = userRequired.getInfo(privacy)
        if field not in info:
            userInfo = {}
            raise PermissionException()
        else:
            userInfo[field] = info[field]
            raise SuccessException(message='Field permitted')

    except SuccessException as e:
        status = int(e)
        message = str(e)
    except ModelException as e:
        status = int(e)
        message = str(e)
    except User.DoesNotExist as e:
        status = 101
        message = str(e)
    except PermissionException as e:
        message = str(e)
        status = int(e)
    except FieldRequiredException as e:
        message = str(e)
        status = int(e)
    except Exception as e:
        message = str(e)
        status = 199

    response['message'] = message
    response['status'] = status
    response['user'] = userInfo
    return JsonResponse(response)


@csrf_exempt
def delete(request):
    password = clear(request.POST.get('password', None))
    token = clear(request.POST.get('token', None))

    response = {}
    message = 'Exception'
    status = 199

    try:
        if token is None:
            raise FieldRequiredException(field='token')
        if password is None:
            raise FieldRequiredException(field='password')

        user = User.objects.get(token=token)

        if user.validatePassword(password):
            user.preDelete()
            raise SuccessException(message='User deleted')
        else:
            raise ModelException(message='Wrong password',
                                 status=102)

    except SuccessException as e:
        status = int(e)
        message = str(e)
    except ModelException as e:
        status = int(e)
        message = str(e)
    except User.DoesNotExist as e:
        status = 101
        message = str(e)
    except PermissionException as e:
        message = str(e)
        status = int(e)
    except FieldRequiredException as e:
        message = str(e)
        status = int(e)
    except Exception as e:
        message = str(e)
        status = 199

    response['message'] = message
    response['status'] = status
    response['user'] = {}
    return JsonResponse(response)


@csrf_exempt
def recover(request):
    password = clear(request.POST.get('password', None))
    login = clear(request.POST.get('login', None))

    response = {}
    message = 'Exception'
    status = 199
    userInfo = {}

    try:

        if login is None:
            raise FieldRequiredException(field='login')
        if password is None:
            raise FieldRequiredException(field='password')

        user = User.objects.get(Q(email=login) | Q(nicknme=login))

        if user.validatePassword(password):
            user.recover()
            userInfo = user.getInfo(Type.PRIVATE)
            raise SuccessException(message='User recovered')
        else:
            raise ModelException(message='Wrong password', status=102)

    except SuccessException as e:
        status = int(e)
        message = str(e)
    except ModelException as e:
        status = int(e)
        message = str(e)
    except User.DoesNotExist as e:
        status = 101
        message = str(e)
    except PermissionException as e:
        message = str(e)
        status = int(e)
    except FieldRequiredException as e:
        message = str(e)
        status = int(e)
    except Exception as e:
        message = str(e)
        status = 199

    response['message'] = message
    response['status'] = status
    response['user'] = userInfo
    return JsonResponse(response)


@csrf_exempt
def setAvatar(request):
    token = clear(request.POST.get('token', None))

    response = {}
    message = 'Exception'
    status = 199
    userInfo = {}

    try:
        if token is None:
            raise FieldRequiredException(field='token')

        image = request.FILES['avatar']
        user = User.objects.get(token=token)

        user.setAvatar(image)
        raise SuccessException(message='Avatar uploaded')
    except SuccessException as e:
        message = str(e)
        status = int(e)
    except User.DoesNotExist as e:
        message = str(e)
        status = 101
    except FieldRequiredException as e:
        message = str(e)
        status = int(e)
    except Exception as e:
        message = str(e)
        status = 199

    response['message'] = message
    response['status'] = status
    response['user'] = userInfo
    return JsonResponse(response)


@csrf_exempt
def fillFridge(request):
    products = clear(request.POST.get('products', None))
    token = clear(request.POST.get('token', None))

    response = {}
    userInfo = {}

    try:
        if token is None:
            raise FieldRequiredException('Token')
        if products is None:
            raise FieldRequiredException('Products')

        user = User.objects.get(token=token)
        response = user.deleteFromFridge(products)

        if response['status'] == -1:
            raise ModelException(message='Wrong products id', status=199)
        else:
            raise SuccessException(message='Products added to fridge')

    except SuccessException as e:
        status = int(e)
        message = str(e)
    except ModelException as e:
        status = int(e)
        message = str(e)
    except User.DoesNotExist as e:
        status = 101
        message = str(e)
    except PermissionException as e:
        message = str(e)
        status = int(e)
    except FieldRequiredException as e:
        message = str(e)
        status = int(e)
    except Exception as e:
        message = str(e)
        status = 199

    response['message'] = message
    response['status'] = status
    response['user'] = userInfo
    return JsonResponse(response)


@csrf_exempt
def deleteFromFridge(request):
    product = clear(request.POST.get('id', None))
    token = clear(request.POST.get('token', None))

    response = {}
    userInfo = {}

    try:
        if token is None:
            raise FieldRequiredException('Token')
        if product is None:
            raise FieldRequiredException('Product')

        user = User.objects.get(token=token)
        response = user.deleteFromFridge(product)

        if response['status'] == -1:
            raise ModelException(message='Wrong product id', status=199)
        else:
            raise SuccessException(message='Product deleted from fridge')

    except SuccessException as e:
        status = int(e)
        message = str(e)
    except ModelException as e:
        status = int(e)
        message = str(e)
    except User.DoesNotExist as e:
        status = 101
        message = str(e)
    except PermissionException as e:
        message = str(e)
        status = int(e)
    except FieldRequiredException as e:
        message = str(e)
        status = int(e)
    except Exception as e:
        message = str(e)
        status = 199

    response['message'] = message
    response['status'] = status
    response['user'] = userInfo
    return JsonResponse(response)


@csrf_exempt
def banIngredient(request):
    product = clear(request.POST.get('id', None))
    token = clear(request.POST.get('token', None))

    response = {}
    userInfo = {}

    try:
        if token is None:
            raise FieldRequiredException('Token')
        if product is None:
            raise FieldRequiredException('Product')

        user = User.objects.get(token=token)
        response = user.banIngredient(product)

        if response['status'] == -1:
            raise ModelException(message='Wrong product id', status=199)
        else:
            raise SuccessException(message='Product blocked')

    except SuccessException as e:
        status = int(e)
        message = str(e)
    except ModelException as e:
        status = int(e)
        message = str(e)
    except User.DoesNotExist as e:
        status = 101
        message = str(e)
    except PermissionException as e:
        message = str(e)
        status = int(e)
    except FieldRequiredException as e:
        message = str(e)
        status = int(e)
    except Exception as e:
        message = str(e)
        status = 199

    response['message'] = message
    response['status'] = status
    response['user'] = userInfo
    return JsonResponse(response)


@csrf_exempt
def unblockIngredient(request):
    product = clear(request.POST.get('id', None))
    token = clear(request.POST.get('token', None))

    response = {}
    userInfo = {}

    try:
        if token is None:
            raise FieldRequiredException('Token')
        if product is None:
            raise FieldRequiredException('Product')

        user = User.objects.get(token=token)
        response = user.unblockIngredient(product)

        if response['status'] == -1:
            raise ModelException(message='Wrong product id', status=199)
        else:
            raise SuccessException(message='Product unblocked')

    except SuccessException as e:
        status = int(e)
        message = str(e)
    except ModelException as e:
        status = int(e)
        message = str(e)
    except User.DoesNotExist as e:
        status = 101
        message = str(e)
    except PermissionException as e:
        message = str(e)
        status = int(e)
    except FieldRequiredException as e:
        message = str(e)
        status = int(e)
    except Exception as e:
        message = str(e)
        status = 199

    response['message'] = message
    response['status'] = status
    response['user'] = userInfo
    return JsonResponse(response)


@csrf_exempt
def banRecipe(request):
    recipe = clear(request.POST.get('id', None))
    token = clear(request.POST.get('token', None))

    response = {}
    userInfo = {}

    try:
        if token is None:
            raise FieldRequiredException('Token')
        if recipe is None:
            raise FieldRequiredException('Recipe')

        user = User.objects.get(token=token)
        response = user.banRecipe(recipe)

        if response['status'] == -1:
            raise ModelException(message='Wrong recipe id', status=199)
        else:
            raise SuccessException(message='Recipe blocked')

    except SuccessException as e:
        status = int(e)
        message = str(e)
    except ModelException as e:
        status = int(e)
        message = str(e)
    except User.DoesNotExist as e:
        status = 101
        message = str(e)
    except PermissionException as e:
        message = str(e)
        status = int(e)
    except FieldRequiredException as e:
        message = str(e)
        status = int(e)
    except Exception as e:
        message = str(e)
        status = 199

    response['message'] = message
    response['status'] = status
    response['user'] = userInfo
    return JsonResponse(response)


@csrf_exempt
def unblockRecipe(request):
    recipe = clear(request.POST.get('id', None))
    token = clear(request.POST.get('token', None))

    response = {}
    userInfo = {}

    try:
        if token is None:
            raise FieldRequiredException('Token')
        if recipe is None:
            raise FieldRequiredException('Recipe')

        user = User.objects.get(token=token)
        response = user.unblockRecipe(recipe)

        if response['status'] == -1:
            raise ModelException(message='Wrong recipe id', status=199)
        else:
            raise SuccessException(message='Recipe unblocked')

    except SuccessException as e:
        status = int(e)
        message = str(e)
    except ModelException as e:
        status = int(e)
        message = str(e)
    except User.DoesNotExist as e:
        status = 101
        message = str(e)
    except PermissionException as e:
        message = str(e)
        status = int(e)
    except FieldRequiredException as e:
        message = str(e)
        status = int(e)
    except Exception as e:
        message = str(e)
        status = 199

    response['message'] = message
    response['status'] = status
    response['user'] = userInfo
    return JsonResponse(response)


@csrf_exempt
def starIngredient(request):
    product = clear(request.POST.get('id', None))
    token = clear(request.POST.get('token', None))

    response = {}
    userInfo = {}

    try:
        if token is None:
            raise FieldRequiredException('Token')
        if product is None:
            raise FieldRequiredException('Product')

        user = User.objects.get(token=token)
        response = user.unstarIngredient(product)

        if response['status'] == -1:
            raise ModelException(message='Wrong product id', status=199)
        else:
            raise SuccessException(message='Product added to starred')

    except SuccessException as e:
        status = int(e)
        message = str(e)
    except ModelException as e:
        status = int(e)
        message = str(e)
    except User.DoesNotExist as e:
        status = 101
        message = str(e)
    except PermissionException as e:
        message = str(e)
        status = int(e)
    except FieldRequiredException as e:
        message = str(e)
        status = int(e)
    except Exception as e:
        message = str(e)
        status = 199

    response['message'] = message
    response['status'] = status
    response['user'] = userInfo
    return JsonResponse(response)


@csrf_exempt
def unstarIngredient(request):
    product = clear(request.POST.get('id', None))
    token = clear(request.POST.get('token', None))

    response = {}
    userInfo = {}

    try:
        if token is None:
            raise FieldRequiredException('Token')
        if product is None:
            raise FieldRequiredException('Product')

        user = User.objects.get(token=token)
        response = user.unstarIngredient(product)

        if response['status'] == -1:
            raise ModelException(message='Wrong product id', status=199)
        else:
            raise SuccessException(message='Product removed from starred')

    except SuccessException as e:
        status = int(e)
        message = str(e)
    except ModelException as e:
        status = int(e)
        message = str(e)
    except User.DoesNotExist as e:
        status = 101
        message = str(e)
    except PermissionException as e:
        message = str(e)
        status = int(e)
    except FieldRequiredException as e:
        message = str(e)
        status = int(e)
    except Exception as e:
        message = str(e)
        status = 199

    response['message'] = message
    response['status'] = status
    response['user'] = userInfo
    return JsonResponse(response)


@csrf_exempt
def starRecipe(request):
    recipe = clear(request.POST.get('id', None))
    token = clear(request.POST.get('token', None))

    response = {}
    userInfo = {}

    try:
        if token is None:
            raise FieldRequiredException('Token')
        if recipe is None:
            raise FieldRequiredException('Recipe')

        user = User.objects.get(token=token)
        response = user.starRecipe(recipe)

        if response['status'] == -1:
            raise ModelException(message='Wrong recipe id', status=199)
        else:
            raise SuccessException(message='Recipe added to starred')

    except SuccessException as e:
        status = int(e)
        message = str(e)
    except ModelException as e:
        status = int(e)
        message = str(e)
    except User.DoesNotExist as e:
        status = 101
        message = str(e)
    except PermissionException as e:
        message = str(e)
        status = int(e)
    except FieldRequiredException as e:
        message = str(e)
        status = int(e)
    except Exception as e:
        message = str(e)
        status = 199

    response['message'] = message
    response['status'] = status
    response['user'] = userInfo
    return JsonResponse(response)


@csrf_exempt
def unstarRecipe(request):
    recipe = clear(request.POST.get('id', None))
    token = clear(request.POST.get('token', None))

    response = {}
    userInfo = {}

    try:
        if token is None:
            raise FieldRequiredException('Token')
        if recipe is None:
            raise FieldRequiredException('Recipe')

        user = User.objects.get(token=token)
        response = user.unstarRecipe(recipe)

        if response['status'] == -1:
            raise ModelException(message='Wrong recipe id', status=199)
        else:
            raise SuccessException(message='Recipe removed from starred')

    except SuccessException as e:
        status = int(e)
        message = str(e)
    except ModelException as e:
        status = int(e)
        message = str(e)
    except User.DoesNotExist as e:
        status = 101
        message = str(e)
    except PermissionException as e:
        message = str(e)
        status = int(e)
    except FieldRequiredException as e:
        message = str(e)
        status = int(e)
    except Exception as e:
        message = str(e)
        status = 199

    response['message'] = message
    response['status'] = status
    response['user'] = userInfo
    return JsonResponse(response)


@csrf_exempt
def verifyUser(request):
    code = clear(request.POST.get('code', None))
    token = clear(request.POST.get('token', None))

    response = {}
    userInfo = {}

    try:
        if token is None:
            raise FieldRequiredException('Token')
        if code is None:
            raise FieldRequiredException('Code')

        user = User.objects.get(token=token)

        if user.verifyCode(code):
            userInfo = user.getInfo(Type.PRIVATE)
            raise SuccessException(message='Account verified')
        else:
            raise ModelException(message='Wrong code', status=102)

    except SuccessException as e:
        status = int(e)
        message = str(e)
    except ModelException as e:
        status = int(e)
        message = str(e)
    except User.DoesNotExist as e:
        status = 101
        message = str(e)
    except PermissionException as e:
        message = str(e)
        status = int(e)
    except FieldRequiredException as e:
        message = str(e)
        status = int(e)
    except Exception as e:
        message = str(e)
        status = 199

    response['message'] = message
    response['status'] = status
    response['user'] = userInfo
    return JsonResponse(response)


def verificationCode(request):
    token = request.GET.get('token', None)

    response = {}
    userInfo = {}

    try:
        if token is None:
            raise Exception('Token required')

        token = "".join(token.split('"'))
        user = User.objects.get(token=token)
        code = user.generateCode()

        if sendVerificationMail(code=code, email=user.email, name=user.name):
            raise SuccessException(message='Verification code has been sent')
        else:
            raise ModelException(message='Verification code has not been sent', status=199)

    except SuccessException as e:
        status = int(e)
        message = str(e)
    except ModelException as e:
        status = int(e)
        message = str(e)
    except User.DoesNotExist as e:
        status = 101
        message = str(e)
    except PermissionException as e:
        message = str(e)
        status = int(e)
    except FieldRequiredException as e:
        message = str(e)
        status = int(e)
    except Exception as e:
        message = str(e)
        status = 199

    response['message'] = message
    response['status'] = status
    response['user'] = userInfo
    return JsonResponse(response)


def recoveryPasswordGet(request):
    login = clear(request.GET.get('login', None))

    response = {}
    userInfo = {}
    status = 101

    try:
        if login is None:
            raise FieldRequiredException('Login (email or nickname)')

        user = User.objects.get(Q(email=login) | Q(nickname=login))
        code = user.generateCode(length=5, type=Type.PRIVATE)

        st = sendRecoveryMail(email=user.email, code=code, name=user.name)
        if st:
            raise SuccessException(message='Password changed')
        else:
            raise Exception('Recovery code has not been sent')

    except SuccessException as e:
        status = int(e)
        message = str(e)
    except ModelException as e:
        status = int(e)
        message = str(e)
    except User.DoesNotExist as e:
        status = 101
        message = str(e)
    except PermissionException as e:
        message = str(e)
        status = int(e)
    except FieldRequiredException as e:
        message = str(e)
        status = int(e)
    except Exception as e:
        message = str(e)
        status = 199

    response['message'] = message
    response['status'] = status
    response['user'] = userInfo
    return JsonResponse(response)


@csrf_exempt
def recoveryPasswordPost(request):
    code = clear(request.POST.get('code', None))
    login = clear(request.POST.get('login', None))
    password = clear(request.POST.get('password', None))

    response = {}
    userInfo = {}
    try:
        if code is None:
            raise FieldRequiredException('Code')
        if login is None:
            raise FieldRequiredException('Login (email or nickname)')
        if password is None:
            raise FieldRequiredException('New password')

        user = User.objects.get(Q(email=login) | Q(nickname=login))

        if user.recoveryCode == code:
            user.setPassword(password)
            user.generateToken(user.getInfo(Type.PRIVATE))
            user.recoveryCode = ""
            user.save()
            userInfo = user.getInfo(Type.PRIVATE)
            raise SuccessException(message='Password changed')
        else:
            raise ModelException(message='Wrong code', status=102)

    except SuccessException as e:
        status = int(e)
        message = str(e)
    except ModelException as e:
        status = int(e)
        message = str(e)
    except User.DoesNotExist as e:
        status = 101
        message = str(e)
    except PermissionException as e:
        message = str(e)
        status = int(e)
    except FieldRequiredException as e:
        message = str(e)
        status = int(e)
    except Exception as e:
        message = str(e)
        status = 199

    response['message'] = message
    response['status'] = status
    response['user'] = userInfo
    return JsonResponse(response)


def check_login(request):
    login = request.GET.get('login', None)

    response = {}

    try:
        user = User.objects.get(Q(email=login) | Q(nickname=login))
        if user.nickname == login:
            raise RejectException(field='nickname', status=107)
        else:
            raise RejectException(field='email', status=108)
    except User.DoesNotExist:
        message = 'Login available'
        status = 100
    except RejectException as e:
        message = str(e)
        status = int(e)

    response['message'] = message
    response['status'] = status
    return JsonResponse(response)

