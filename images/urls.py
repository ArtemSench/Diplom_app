from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    path('upload/', upload_image, name='upload_image'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('delete_image/<int:image_id>/', delete_image, name='delete_image'),
]