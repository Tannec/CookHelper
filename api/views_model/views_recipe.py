from datetime import datetime
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from api.models import Recipe, User

from api.views_model.static_functions import clear


@csrf_exempt
def createRecipe(request):
    try:
        data = clear(request.POST.dict())
        recipe = Recipe()

        response = recipe.create(data)

    except Exception as e:
        response = {'message': str(e), 'status': -1}
    return JsonResponse(response)


@csrf_exempt
def getInformation(request):
    token = clear(request.GET.get('token', None))
    id = clear(request.GET.get('id', None))

    try:
        if token is None:
            raise Exception('Token required')
        if id is None:
            raise Exception('Recipe id recuired')

        response = {}

        # TODO

    except Exception as e:
        response = {'message': str(e), 'status': -1}
    return JsonResponse(response)
