from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from api.views_model.views_user import *
from api.views_model.views_forum import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user/post/auth/', authorize),
    path('api/user/post/reg/', register),
    path('api/user/post/avatar/', setAvatar),
    path('api/user/post/password/', changePassword),
    path('api/user/get/', info),
    path('api/user/post/delete/', delete),
    path('api/user/post/recover/', recover),
    path('api/user/post/fridge/add/', fillFridge),
    path('api/user/post/fridge/delete/', deleteFromFridge),
    path('api/user/post/starred-recipes/add/', starRecipe),
    path('api/user/post/starred-recipes/delete/', unstarRecipe),
    path('api/user/post/banned-recipes/add/', banRecipe),
    path('api/user/post/banned-recipes/delete/', unblockRecipe),
    path('api/user/post/starred-product/add/', starIngredient),
    path('api/user/post/starred-product/delete/', unstarIngredient),
    path('api/user/post/banned-product/add/', banIngredient),
    path('api/user/post/banned-product/delete/', unblockIngredient),
    path('api/user/post/verify/', verifyUser),

    path('api/forum/post/create/', createForum),
    path('api/forum/get/', getInfo),
    path('api/forum/post/add-member/', addMember),
    path('api/forum/post/delete-member/', deleteMember),
    path('api/forum/post/message/', addMessage),

]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
