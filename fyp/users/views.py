from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django import forms
from .forms import UserRegisterForm, UploadFileForm
from django.core.files.storage import FileSystemStorage
from django.core.files.storage import default_storage
import numpy as np
import pandas as pd
import os

# Create your views here.
def index(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created! You are now able to log in!')
            return redirect('users:login')
    else:
        form = UserRegisterForm()

    title = 'Register New User'
    return render(request, 'users/register.html', {'form': form, 'title': title})

@login_required
def profile(request):
    return render(request, 'users/profile.html')

def upload_datafiles(request):
    templates = 'users/upload.html'

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_files = request.FILES['file']
            fs = FileSystemStorage()
            fs.save(uploaded_files.name, uploaded_files)
            messages.success(request, f'File Uploaded!')
            return render(request, templates, {'form': form})           
    else:
        form = UploadFileForm()

    return render(request, templates, {'form': form})

def read_data(request):
    templates = 'users/read.html'

    pd.set_option('display.width', 1000)
    pd.set_option('colheader_justify', 'center')

    df = pd.read_csv('media/titanic_test.csv')
    data_html = df.to_html(table_id='dtBasicExample', classes="table table-striped table-bordered")

    return render(request, templates, {'data': data_html})

def test(request):
    templates = 'users/test.html'

    df = pd.read_csv('media/titanic_test.csv')
    columns = df.columns.values

    return render(request, templates, {'columns' : columns})






    


