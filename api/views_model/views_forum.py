from datetime import datetime
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from api.models import Forum, User, TextMessage

@csrf_exempt
def addMember(request):
    forumId = request.POST.get('id', None)
    token = request.POST.get('token', None)
    if token is None:
        response = {"message": "Wrong token", "status": -1}
    else:
        try:
            user = User.objects.get(token=token)
            if forumId is None:
                response = {"message": "Topic required", "status": -1}
            else:
                forum = Forum.objects.get(forumId)
                forum.addMember(user.id)
        except Exception as e:
            response = {"message": "Wrong token or topic id", "exception": str(e), "status": -1}
    return JsonResponse(response)

@csrf_exempt
def deleteMember(request):
    forumId = request.POST.get('id', None)
    token = request.POST.get('token', None)
    if token is None:
        response = {"message": "Wrong token", "status": -1}
    else:
        try:
            user = User.objects.get(token=token)
            if forumId is None:
                response = {"message": "Topic required", "status": -1}
            else:
                forum = Forum.objects.get(forumId)
                forum.deleteMember(user.id)
            return JsonResponse(response)
        except Exception as e:
            response = {"message": "Wrong token or topic id", "exception": str(e), "status": -1}
            return JsonResponse(response)
    return JsonResponse(response)

@csrf_exempt
def addMessage(request):
    forumId = request.POST.get('id', None)
    token = request.POST.get('token', None)
    textMessage = request.POST.get('message', None)
    try:
        user = User.objects.get(token=token)
        if forumId is None:
            response = {"message": "Topic id required", "status": -1}
        else:
            forum = Forum.objects.get(forumId)
            message = TextMessage()
            message.text = textMessage
            message.userId = user.id
            message.time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            message.save()
            forum.addMessage(message.id)
            response = {"message": "Message added", "status": -1}
        return JsonResponse(response)
    except Exception as e:
        response = {"message": "Wrong token or forum id", "exception": str(e), "status": -1}
        return JsonResponse(response)

@csrf_exempt
def createForum(request):
    token = request.POST.get('token', None)
    title = request.POST.get('title', None)
    if token is None:
        response = {"message": "Wrong token", "status": -1}
    else:
        if title is None:
            response = {"message": "Wrong title", "status": -1}
        else:
            try:
                user = User.objects.get(token=token)
                forum = Forum()
                forum.title = title
                forum.owner = user.id
                forum.save()
                response = {"message": "Topic created", "id": forum.id, "status": 1}
            except Exception as e:
                response = {"message": "Wrong token", "exception": str(e), "status": -1}
    return JsonResponse(response)


def getInfo(request):
    forumId = request.GET.get('id', None)
    try:
        forum = Forum.objects.get(id=forumId)
        response = {'message': 'Topic info', 'topic': {'messages': forum.messages, 'owner': forum.owner, 'members': forum.members}}
    except Exception as e:
        response = {"message": "Wrong forum id", "exception": str(e), "status": -1}
    return JsonResponse(response)

@csrf_exempt
def deleteForum(request):
    token = request.POST.get('token', None)
    forumId = request.POST.get('id', None)
    try:
        if token is None:
            raise Exception('Token required')
        if forumId is None:
            raise Exception('Forum id required')
        forum = Forum.objects.get(id=id)
        forum.preDelete()
        response = {'message': 'Topic closed', 'status': -1, 'topic': {}}
    except Exception as e:
        response = {'message': str(e), 'status': -1, 'topic': {}}
    return JsonResponse(response)