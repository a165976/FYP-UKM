from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from .models import Project, Dataset
from .forms import ProjectForm, DataForm
from django import forms
from django.views.generic import (
	ListView, 
	DetailView,
	CreateView,
	UpdateView,
	DeleteView
)
import numpy as np
import pandas as pd


# Create your views here.

class ProjectListView(ListView):
    model = Project
    template_name = 'project/list.html'
    context_object_name = 'projects'
    paginate_by = 5

def ProjectCreateView(request):
    if request.method == "POST":
        p_form = ProjectForm(request.POST)
        d_form = DataForm(request.POST, request.FILES)

        if p_form.is_valid() and d_form.is_valid():
            uploaded_files = request.FILES['dataset']
            df = pd.read_csv(uploaded_files)
            Project = p_form.save(False)
            Project.author = request.user
            Project.save()
            Dataset = d_form.save(False)

            Dataset.title = uploaded_files.name
            Dataset.size = uploaded_files.size
            Dataset.columns = df.columns.values
            Dataset.project = Project
            Dataset.save()
            
            return redirect('project:list')
    else:
        p_form = ProjectForm
        d_form = DataForm

    return render(request, 'project/newproject.html', {'dataform' : p_form, 'projectform' : d_form})

def plotGraph(request,pk):

    #-------------Create tuple pairs for choicefield---------------------
    data = Dataset.objects.get(project=pk)
    columns = data.columns[1:-1]
    remove = columns.replace("'",'')
    choicelist = str.split(remove)
    choicelist2 = choicelist
    choice = list(zip(choicelist,choicelist2))

    graphType = [
        ('line', 'Line'),
        ('bar', 'Bar'),
    ]

    class graphForm(forms.Form):
        x = forms.ChoiceField(choices=choice)
        y = forms.ChoiceField(choices=choice)
        shape = forms.ChoiceField(choices=graphType)

    form = graphForm()


    return render(request, 'project/test.html', {'form': form})



