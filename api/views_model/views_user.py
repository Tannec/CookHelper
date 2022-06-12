import json
from django.db.models import Q
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics
from api.post_service.service import sendVerificationMail, sendRecoveryMail
from api.views_model.static_functions import clear
from api.views_model.static_functions import FieldRequiredException, MissFields, RejectException, PermissionException, \
    ModelException, UnknownField, SuccessException
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
            user.generateToken(user.getInfo(1))
            user.setPassword(new_password)
            SuccessException(message='Password changed')
            userInfo = user.getInfo(Type.PRIVATE)
        else:
            ModelException(status=102,
                           message='Wrong password')

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
def register(request):
    data = clear(request.POST.dict())
    return JsonResponse({'message': f'{data}', 'status': 199, 'user': {}})
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
            SuccessException(message='Registered')
        else:
            SuccessException(message='Code has not been sent')

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
            SuccessException(message='Field permitted')

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
            ModelException(message='Wrong password',
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
            FieldRequiredException(field='token')
        image = request.FILES['image']
        user = User.objects.get(token=token)
        user.setAvatar(image)
        response = {"message": "Avatar uploaded", "status": 1, 'user': {}}
    except Exception as e:
        response = {"message": "Wrong params", "exception": str(e), "status": -1, 'user': {}}


    return JsonResponse(response)


@csrf_exempt
def fillFridge(request):
    products = clear(request.POST.get('products', None))
    token = clear(request.POST.get('token', None))
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


@csrf_exempt
def deleteFromFridge(request):
    products = clear(request.POST.get('products', None))
    token = clear(request.POST.get('token', None))
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


@csrf_exempt
def banIngredient(request):
    product = clear(request.POST.get('product', None))
    token = clear(request.POST.get('token', None))
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


@csrf_exempt
def unblockIngredient(request):
    product = clear(request.POST.get('product', None))
    token = clear(request.POST.get('token', None))
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


@csrf_exempt
def banRecipe(request):
    recipe = clear(request.POST.get('recipe', None))
    token = clear(request.POST.get('token', None))
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


@csrf_exempt
def unblockRecipe(request):
    recipe = clear(request.POST.get('id', None))
    token = clear(request.POST.get('token', None))
    status = 101
    try:
        if token is None:
            status = 104
            raise Exception('Token required')
        if recipe is None:
            status = 104
            raise Exception('Product id required')

        user = User.objects.get(token=token)
        response = user.unblockRecipe(recipe)

        if response['status'] == -1:
            status = 102
        else:
            status = 100

    except Exception as e:
        response = {"message": str(e), 'user': {}}
    response['status'] = status
    return JsonResponse(response)


@csrf_exempt
def starIngredient(request):
    status = 101
    product = clear(request.POST.get('id', None))
    token = clear(request.POST.get('token', None))
    try:
        if token is None:
            status = 104
            raise Exception('Token required')
        if product is None:
            status = 104
            raise Exception('Product id required')

        user = User.objects.get(token=token)
        response = user.starIngredient(product)

        if response['status'] == -1:
            status = 102
        else:
            status = 100

    except Exception as e:
        response = {"message": str(e), 'user': {}}
    response['status'] = status
    return JsonResponse(response)


@csrf_exempt
def unstarIngredient(request):
    status = 101
    product = clear(request.POST.get('id', None))
    token = clear(request.POST.get('token', None))
    try:
        if token is None:
            status = 104
            raise Exception('Token required')
        if product is None:
            status = 104
            raise Exception('Product id required')

        user = User.objects.get(token=token)
        response = user.unstarIngredient(product)

        if response['status'] == -1:
            status = 102
        else:
            status = 100

    except Exception as e:
        response = {'message': str(e), 'user': {}}
    response['status'] = status
    return JsonResponse(response)


@csrf_exempt
def starRecipe(request):
    recipe = clear(request.POST.get('id', None))
    token = clear(request.POST.get('token', None))
    status = 101
    try:

        if token is None:
            status = 104
            raise Exception('Token required')
        if recipe is None:
            status = 104
            raise Exception('Recipe id required')

        user = User.objects.get(token=token)
        response = user.starRecipe(recipe)

        if response['status'] == -1:
            status = 102
        else:
            status = 100

    except Exception as e:
        response = {'message': str(e)}
    response['status'] = status
    response['user'] = {}
    return JsonResponse(response)


@csrf_exempt
def unstarRecipe(request):
    recipe = clear(request.POST.get('id', None))
    token = clear(request.POST.get('token', None))
    status = 101
    try:
        if token is None:
            status = 104
            raise Exception('Token requied')
        if recipe is None:
            status = 104
            raise Exception('Recipe id required')

        user = User.objects.get(token=token)
        response = user.unstarRecipe(recipe)

        if response['status'] == -1:
            status = 102
        else:
            status = 100

    except Exception as e:
        response = {'message': str(e), 'user': {}}
    response['status'] = status
    return JsonResponse(response)


@csrf_exempt
def verifyUser(request):
    code = clear(request.POST.get('code', None))
    token = clear(request.POST.get('token', None))
    status = 101
    try:
        if token is None:
            status = 104
            raise Exception('Token required')
        if code is None:
            status = 104
            raise Exception('Code required')

        user = User.objects.get(token=token)

        if user.verifyCode(code):
            status = 100
            response = {'message': 'Account verified', 'user': user.getInfo(Type.PRIVATE)}
        else:
            status = 102
            response = {'message': 'Wrong code', 'user': {}}
    except Exception as e:
        response = {'message': str(e), 'user': {}}
    response['status'] = status
    return JsonResponse(response)


def verificationCode(request):
    token = request.GET.get('token', None)
    status = 101
    try:
        if token is None:
            raise Exception('Token required')

        token = "".join(token.split('"'))
        user = User.objects.get(token=token)
        code = user.generateCode()

        if sendVerificationMail(code=code, email=user.email, name=user.name):
            status = 100
            response = {'message': 'Verification code has been sent'}
        else:
            status = 199
            response = {'message': 'Verification code has not been sent'}
    except Exception as e:
        status = 199
        response = {'message': str(e)}
    response['status'] = status
    response['user'] = {}
    return JsonResponse(response)


def recoveryPasswordGet(request):
    login = clear(request.GET.get('login', None))
    response = {}
    status = 101
    try:
        if login is None:
            status = 104
            raise Exception('Login (email or nickname) required')
        user = User.objects.get(Q(email=login) | Q(nickname=login))
        code = user.generateCode(length=5, type=Type.PRIVATE)
        st = sendRecoveryMail(email=user.email, code=code, name=user.name)
        if st:
            status = 100
            response = {'message': 'Mail sent', 'user': {}}
        else:
            status = 199
            response = {'message': 'Mail not sent', 'user': {}}
    except Exception as e:
        response = {'message': str(e), 'user': {}}
    response['status'] = status
    return JsonResponse(response)


def recoveryPasswordPost(request):
    code = clear(request.POST.get('code', None))
    login = clear(request.POST.get('login', None))
    password = clear(request.POST.get('password', None))
    response = {}
    status = 101
    try:
        if code is None:
            status = 104
            raise Exception('Code required')
        if login is None:
            status = 104
            raise Exception('Login (email or nickname) required')
        if password is None:
            status = 104
            raise Exception('New password required')
        user = User.objects.get(Q(email=login) | Q(nickname=login))
        st = (user.recoveryCode == code)
        if st:
            user.setPassword(password)
            user.generateToken(user.getInfo(Type.PRIVATE))
            user.recoveryCode = ""
            user.save()
            status = 100
            response = {'message': 'Password changed', 'user': {}}
        else:
            status = 102
            response = {'message': 'Wrong code', 'user': {}}
    except Exception as e:
        response = {'message': str(e), 'user': {}}
    response['status'] = status
    return JsonResponse(response)

