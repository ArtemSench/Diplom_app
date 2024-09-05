from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm, ImageUploadForm
from .models import UploadedImage
import cv2
import numpy as np
import os
from django.conf import settings

def home(request):
    return render(request, 'home.html')

def logout_view(request):
    logout(request)  # Выход пользователя
    return redirect('home')  # Перенаправление на страницу входа (или на другую страницу)

# Загрузка модели
def load_model():
    net = cv2.dnn.readNetFromCaffe(
        os.path.join(settings.BASE_DIR, 'MobileNetSSD_deploy.prototxt'),
        os.path.join(settings.BASE_DIR, 'MobileNetSSD_deploy.caffemodel'))
    return net


model = load_model()

CLASS_NAMES = [
    "background", "aeroplane", "bicycle", "bird", "boat", "bottle",
    "bus", "car", "cat", "chair", "cow", "diningtable", "dog",
    "horse", "motorbike", "person", "pottedplant", "sheep", "sofa",
    "train", "tvmonitor"
]


@login_required
def dashboard(request):
    images = UploadedImage.objects.filter(user=request.user)
    return render(request, 'dashboard.html', {'images': images})


@login_required
def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_image = form.save(commit=False)
            uploaded_image.user = request.user
            uploaded_image.save()
            process_image(uploaded_image)
            return redirect('dashboard')
    else:
        form = ImageUploadForm()
    return render(request, 'add_image_feed.html', {'form': form})


def process_image(uploaded_image):
    image_path = uploaded_image.image.path
    image = cv2.imread(image_path)
    height, width = image.shape[:2]

    blob = cv2.dnn.blobFromImage(image, 0.007843, (width, height), 127.5)
    model.setInput(blob)
    detections = model.forward()

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.5:  # Порог уверенности
            class_id = int(detections[0, 0, i, 1])
            label = CLASS_NAMES[class_id]
            box = detections[0, 0, i, 3:7] * np.array([width, height, width, height])
            (startX, startY, endX, endY) = box.astype("int")
            cv2.rectangle(image, (startX, startY), (endX, endY), (0, 255, 0), 2)
            cv2.putText(image, f"{label}: {confidence:.2f}", (startX, startY - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            uploaded_image.result = label
            uploaded_image.confidence = confidence
            uploaded_image.save()

    cv2.imwrite(image_path, image)

def delete_image(request, image_id):
    image = get_object_or_404(UploadedImage, id=image_id)
    if request.method == 'POST':
        image.delete()
        return redirect('dashboard')  # Замените 'image_list' на имя вашего URL для списка изображений
    return render(request, 'confirm_delete.html', {'image': image})



def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegistrationForm()
    return render(request, 'registration.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
    return render(request, 'login.html')
