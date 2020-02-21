from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from .models import Project
from .forms import ProjectForm
from django.views.generic import (
	ListView, 
	DetailView,
	CreateView,
	UpdateView,
	DeleteView
)

# Create your views here.

class ProjectListView(ListView):
    model = Project
    template_name = 'project/list.html'
    context_object_name = 'projects'
    paginate_by = 2

class ProjectCreateView(CreateView):
    model = Project
    template_name = 'project/newproject.html'
    form_class = ProjectForm
    success_url = 'list'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

