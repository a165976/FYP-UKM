from django import forms
from .models import Project, Dataset

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description']

class DataForm(forms.ModelForm):
    class Meta:
        model = Dataset
        fields = ['dataset']
