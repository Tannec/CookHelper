from datetime import datetime
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from api.models import Forum, User, TextMessage


def addMember(request):
    forumId = request.POST.get('forum', None)
    token = request.POST.get('token', None)
    if token is None:
        response = {"message": "Wrong token", "status": -1}
    else:
        try:
            user = User.objects.get(token=token)
            if forumId is None:
                response = {"message": "Forum required", "status": -1}
            else:
                forum = Forum.objects.get(forumId)
                forum.addMember(user.id)
        except Exception as e:
            response = {"message": "Wrong token or forum id", "exception": str(e), "status": -1}
    return JsonResponse(response)


def deleteMember(request):
    forumId = request.POST.get('forum', None)
    token = request.POST.get('token', None)
    if token is None:
        response = {"message": "Wrong token", "status": -1}
    else:
        try:
            user = User.objects.get(token=token)
            if forumId is None:
                response = {"message": "Forum required", "status": -1}
            else:
                forum = Forum.objects.get(forumId)
                forum.deleteMember(user.id)
            return JsonResponse(response)
        except Exception as e:
            response = {"message": "Wrong token or forum id", "exception": str(e), "status": -1}
            return JsonResponse(response)
    return JsonResponse(response)


def addMessage(request):
    forumId = request.POST.get('forum', None)
    token = request.POST.get('token', None)
    textMessage = request.POST.get('message', None)
    try:
        user = User.objects.get(token=token)
        if forumId is None:
            response = {"message": "Forum required", "status": -1}
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
                response = {"message": "Forum created", "id": forum.id, "status": 1}
            except Exception as e:
                response = {"message": "Wrong token", "exception": str(e), "status": -1}
    return JsonResponse(response)


def getInfo(request):
    forumId = request.GET.get('forum', None)
    try:
        forum = Forum.objects.get(id=forumId)
        response = {'message': 'Forum info', 'forum': {'messages': forum.messages, 'owner': forum.owner, 'members': forum.members}}
    except Exception as e:
        response = {"message": "Wrong forum id", "exception": str(e), "status": -1}
    return JsonResponse(response)


def deleteForum