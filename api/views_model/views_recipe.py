from datetime import datetime
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from api.models import Recipe, User


def createRecipe(request):
    token = request.POST.get('token', None)
    title = request.POST.get('title', None)
    steps = request.POST.get('steps', None)
    ingredients = request.POST.get('ingredients', None)
    time = request.POST.get('time', None)
    category = request.POST.get('category', None)
    userId = request.POST.get('userId', None)

    calories = request.POST.get('calories', None)
    carbs = request.POST.get('carbs', None)
    proteins = request.POST.get('proteins', None)
    fats = request.POST.get('fats', None)

    imageStatus = {'image_status': 1}
    try:
        image = request.FIELS['image']
        imageStatus['image_status'] = 1
    except Exception as e:
        image = None
        imageStatus['image_status'] = -1
        imageStatus['exception'] = str(e)

    if token is None:
        return JsonResponse({'message': 'Token required', 'status': -1})
    if title is None or steps is None or ingredients or time is None or category is None or userId is None:
        return JsonResponse({'message': 'All parameters required', 'status': -1})
    try:
        fields = {}
        user = User.objects.get(token=token)
        recipe = Recipe()
        fields['title'] = title
        fields['category'] = category
        fields['steps'] = steps
        fields['ingredients'] = ingredients
        fields['time'] = time
        fields['calories'] = calories
        fields['proteins'] = proteins
        fields['carbs'] = carbs
        fields['fats'] = fats
        fields['userId'] = userId

        recipe.create(fields)
        recipe.save()
        if image is not None:
            recipe.setImage(image)
            recipe.save()
        return JsonResponse(recipe.create(fields))
    except Exception as e:
        return JsonResponse({'message': 'Wrong token', 'status': -1, 'exception': str(e)})
