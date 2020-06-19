from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Project, Dataset, Plot
from .forms import ProjectForm, DataForm
from django import forms
from django.forms import formset_factory
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import HoverTool, ColumnDataSource, CDSView, Line
from bokeh.palettes import Spectral3, Spectral5, Category10
from bokeh.transform import factor_cmap
from bokeh.document import Document
from django.views.generic import (
	ListView, 
	DetailView,
	CreateView,
	UpdateView,
	DeleteView

)
import numpy as np
import pandas as pd
import ast

# Create your views here.

class ProjectListView(ListView):
    model = Project
    template_name = 'project/list.html'
    context_object_name = 'projects'
    paginate_by = 5

@login_required
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
            Dataset.columns = df.columns.str.strip().str.replace(' ','_')
            Dataset.project = Project
            Dataset.save()
            
            return redirect(reverse('project:plot-list', kwargs={'pk': Project.pk}))
    else:
        p_form = ProjectForm
        d_form = DataForm

    return render(request, 'project/newproject.html', {'dataform' : p_form, 'projectform' : d_form})

def plotGraph(request, pk):

    #----------------------import data--------------------------
    data = Dataset.objects.get(project=pk)
    plots = Plot.objects.filter(project=pk)
    title = data.title
    df = pd.read_csv(f'media/datasets/{title}')
    df[df.columns[0]] = pd.to_datetime(df[df.columns[0]])
    df.columns = df.columns.str.strip().str.replace(' ','_')
    dateindex = df.columns.values[0]
    print(df)

    #-------------Create tuple pairs for choicefield---------------------
    choicelist = df.columns.values.tolist()
    choicelist2 = choicelist
    choice = list(zip(choicelist,choicelist2))
    print(choice)
    #------------------Create form------------------------------------
    class LineForm(forms.Form):
        Title = forms.CharField()
        Y = forms.ChoiceField(choices=choice)
        Description = forms.CharField(widget=forms.Textarea)

    class LineForm2(forms.Form):
        Title = forms.CharField()
        Y = forms.ChoiceField(choices=choice)
        Y2 = forms.ChoiceField(choices=choice)
        Description = forms.CharField(widget=forms.Textarea)

    form = LineForm()
    form2 = LineForm2()

    # class BarChartForm(forms.Form):
    #     Y = forms.ChoiceField(choices=choice)
    #     X = forms.ChoiceField(choices=choice)
    # form3 = BarChartForm()
    
    #-----------------------------CreatePlot--------------------------#
    
    if request.method == 'POST' and 'createdouble' in request.POST:
        form2 = LineForm2(request.POST)
        if form2.is_valid():
            print('doubleline')
            source = ColumnDataSource(df)
            TOOLS = 'save,pan,box_zoom,reset,wheel_zoom'
            p = figure(
                title= form2.cleaned_data['Title'],
                x_axis_type='datetime', 
                tools=TOOLS, 
                plot_height=400, 
                plot_width=700,
                )
            p.xaxis.axis_label = 'Time'
            # p.yaxis.axis_label = form.cleaned_data['Y']
            view = CDSView(source=source, filters=[])
            y = form2.cleaned_data['Y']
            y2 = form2.cleaned_data['Y2']
            # p.multi_line(xs="xs", ys="ys", source=source, line_color="color",legend_group='group', view=view, line_width=2)
            line1 = p.line(x=df.columns.values[0], y=y, source=source, color=Spectral3[0], legend_label=y, view=view)
            line2 = p.line(x=df.columns.values[0], y=y2, source=source, color=Spectral3[2], legend_label=y2, view=view)
            line2 = p.line(x=df.columns.values[0], y=y, source=source, alpha = 0)
            hover = HoverTool(
                tooltips = [
                    ('Date', f'@{dateindex}''{%F}'),
                    (f"{form2.cleaned_data['Y']}", f"@{form2.cleaned_data['Y']}"),
                    (f"{form2.cleaned_data['Y2']}", f"@{form2.cleaned_data['Y2']}"),
                ],
                formatters={
                    f'@{dateindex}': 'datetime',
                },
                mode='vline',
                renderers=[line1]
            )
            p.add_tools(hover)
            script, div = components(p) 
            return render(request, 'project/test.html', {'script': script, 'div':div, 'form':form, 'form2':form2, 'type':'Double', 'data':data})


    if request.method == 'POST' and 'createsingle' in request.POST:
        form = LineForm(request.POST)
        if form.is_valid():
            source = ColumnDataSource(df)
            print('singleline')
            TOOLS = 'save,pan,box_zoom,reset,wheel_zoom'
            p = figure(
                title= form.cleaned_data['Title'],
                x_axis_type='datetime', 
                tools=TOOLS, 
                plot_height=400, 
                plot_width=700,
                )
            p.xaxis.axis_label = 'Time'
            p.yaxis.axis_label = form.cleaned_data['Y']
            view = CDSView(source=source, filters=[])
            hover = HoverTool(
                tooltips = [
                    ('Date', f'@{dateindex}''{%F}'),
                    (f"{form.cleaned_data['Y']}", f"@{form.cleaned_data['Y']}"),
                ],
                formatters={
                    f'@{dateindex}': 'datetime',
                },
                mode='vline'
            )
            p.add_tools(hover)
            p.line(x=df.columns.values[0], y=form.cleaned_data['Y'], source=source, view=view)
            script, div = components(p)
            return render(request, 'project/test.html', {'script': script, 'div':div, 'form':form, 'form2':form2, 'type':'Single', 'data':data})
    
    #------------------------------SavePlot-----------------------------------------#

    if request.method == 'POST' and 'savesingle' in request.POST:
        form = LineForm(request.POST)
        if form.is_valid():
            plottype = 'Single'
            plot = Plot()
            plot.project = Project.objects.get(id=pk)
            plot.title = form.cleaned_data['Title']
            plot.columns = form.cleaned_data['Y']
            plot.description = form.cleaned_data['Description']
            plot.plottype = plottype
            plot.save()
            # return render(request, 'project/test.html', {'form':form,'form2':form2, 'data':data})
            return render(request, 'project/plotlist.html', {'plots': plots, 'projectid': pk, 'data':data})

    if request.method == 'POST' and 'savedouble' in request.POST:
        form2 = LineForm2(request.POST)
        if form2.is_valid():
            plottype = 'Double'
            plot = Plot()
            plot.project = Project.objects.get(id=pk)
            plot.title = form2.cleaned_data['Title']
            plot.columns = [form2.cleaned_data['Y'], form2.cleaned_data['Y2']]
            plot.plottype = plottype
            plot.description = form2.cleaned_data['Description']
            plot.save()
            # return render(request, 'project/test.html', {'form':form,'form2':form2, 'data':data})
            return render(request, 'project/plotlist.html', {'plots': plots, 'projectid': pk, 'data':data})
   
    return render(request, 'project/test.html', {'form':form,'form2':form2, 'data':data})

def editPlot(request, pk, plotpk):
    #----------------------import data--------------------------
    data = Dataset.objects.get(project=pk)
    plots = Plot.objects.filter(project=pk) #--------projectplot---------
    currentplot = Plot.objects.get(id=plotpk) #--------currentplot--------
    title = data.title
    df = pd.read_csv(f'media/datasets/{title}')
    df[df.columns[0]] = pd.to_datetime(df[df.columns[0]])
    df.columns = df.columns.str.strip().str.replace(' ','_')
    dateindex = df.columns.values[0]

    #-------------Create tuple pairs for choicefield---------------------
    choicelist = df.columns.values.tolist()
    choicelist2 = choicelist
    choice = list(zip(choicelist,choicelist2))
    #------------------Create form------------------------------------
    class LineForm(forms.Form):
        Title = forms.CharField()
        Y = forms.ChoiceField(choices=choice)
        Description = forms.CharField(widget=forms.Textarea)

    class LineForm2(forms.Form):
        Title = forms.CharField()
        Y = forms.ChoiceField(choices=choice)
        Y2 = forms.ChoiceField(choices=choice)
        Description = forms.CharField(widget=forms.Textarea)

    form = LineForm()
    form2 = LineForm2()

    #-----------------------------CreatePlot--------------------------#
    
    if request.method == 'POST' and 'createdouble' in request.POST:
        form2 = LineForm2(request.POST)
        if form2.is_valid():
            print('doubleline')
            source = ColumnDataSource(df)
            TOOLS = 'save,pan,box_zoom,reset,wheel_zoom'
            p = figure(
                title= form2.cleaned_data['Title'],
                x_axis_type='datetime', 
                tools=TOOLS, 
                plot_height=400, 
                plot_width=700,
                )
            p.xaxis.axis_label = 'Time'
            # p.yaxis.axis_label = form.cleaned_data['Y']
            view = CDSView(source=source, filters=[])
            y = form2.cleaned_data['Y']
            y2 = form2.cleaned_data['Y2']
            # p.multi_line(xs="xs", ys="ys", source=source, line_color="color",legend_group='group', view=view, line_width=2)
            line1 = p.line(x=df.columns.values[0], y=y, source=source, color=Spectral3[0], legend_label=y, view=view)
            line2 = p.line(x=df.columns.values[0], y=y2, source=source, color=Spectral3[2], legend_label=y2, view=view)
            line2 = p.line(x=df.columns.values[0], y=y, source=source, alpha = 0)
            hover = HoverTool(
                tooltips = [
                    ('Date', f'@{dateindex}''{%F}'),
                    (f"{form2.cleaned_data['Y']}", f"@{form2.cleaned_data['Y']}"),
                    (f"{form2.cleaned_data['Y2']}", f"@{form2.cleaned_data['Y2']}"),
                ],
                formatters={
                    f'@{dateindex}': 'datetime',
                },
                mode='vline',
                renderers=[line1]
            )
            p.add_tools(hover)
            script, div = components(p) 
            return render(request, 'project/editplot.html', {'script': script, 'div':div, 'form':form, 'form2':form2, 'type':'Double', 'data':data})

    if request.method == 'POST' and 'createsingle' in request.POST:
        form = LineForm(request.POST)
        if form.is_valid():
            source = ColumnDataSource(df)
            print('singleline')
            TOOLS = 'save,pan,box_zoom,reset,wheel_zoom'
            p = figure(
                title= form.cleaned_data['Title'],
                x_axis_type='datetime', 
                tools=TOOLS, 
                plot_height=400, 
                plot_width=700,
                )
            p.xaxis.axis_label = 'Time'
            p.yaxis.axis_label = form.cleaned_data['Y']
            view = CDSView(source=source, filters=[])
            hover = HoverTool(
                tooltips = [
                    ('Date', f'@{dateindex}''{%F}'),
                    (f"{form.cleaned_data['Y']}", f"@{form.cleaned_data['Y']}"),
                ],
                formatters={
                    f'@{dateindex}': 'datetime',
                },
                mode='vline'
            )
            p.add_tools(hover)
            p.line(x=df.columns.values[0], y=form.cleaned_data['Y'], source=source, view=view)
            script, div = components(p)
            return render(request, 'project/editplot.html', {'script': script, 'div':div, 'form':form, 'form2':form2, 'type':'Single', 'data':data})
    
    #------------------------------SavePlot-----------------------------------------#

    if request.method == 'POST' and 'savesingle' in request.POST:
        form = LineForm(request.POST)
        if form.is_valid():
            plottype = 'Single'
            plot = currentplot = Plot.objects.get(id=plotpk)
            plot.project = Project.objects.get(id=pk)
            plot.title = form.cleaned_data['Title']
            plot.columns = form.cleaned_data['Y']
            plot.description = form.cleaned_data['Description']
            plot.plottype = plottype
            plot.save()
            return redirect(reverse('project:view-plot', kwargs={'pk':pk, 'plotpk':currentplot.id}))
            # return render(request, 'project/plotlist.html', {'plots': plots, 'projectid': pk, 'data':data})

    if request.method == 'POST' and 'savedouble' in request.POST:
        form2 = LineForm2(request.POST)
        if form2.is_valid():
            plottype = 'Double'
            plot = currentplot = Plot.objects.get(id=plotpk)
            plot.project = Project.objects.get(id=pk)
            plot.title = form2.cleaned_data['Title']
            plot.columns = [form2.cleaned_data['Y'], form2.cleaned_data['Y2']]
            plot.plottype = plottype
            plot.description = form2.cleaned_data['Description']
            plot.save()
            return redirect(reverse('project:view-plot', kwargs={'pk':pk, 'plotpk':currentplot.id}))
    
    #----------------------------viewPlot------------------------------#
    if currentplot.plottype == 'Single':
        source = ColumnDataSource(df)
        print('singleline')
        TOOLS = 'save,pan,box_zoom,reset,wheel_zoom'
        p = figure(
            title= currentplot.title,
            x_axis_type='datetime', 
            tools=TOOLS, 
            plot_height=400, 
            plot_width=700,
            )
        p.xaxis.axis_label = 'Time'
        p.yaxis.axis_label = currentplot.columns
        view = CDSView(source=source, filters=[])
        hover = HoverTool(
            tooltips = [
                ('Date', f'@{dateindex}''{%F}'),
                (f"{currentplot.columns}", f"@{currentplot.columns}"),
            ],
            formatters={
                f'@{dateindex}': 'datetime',
            },
            mode='vline'
        )
        p.add_tools(hover)
        p.line(x=df.columns.values[0], y=currentplot.columns, source=source, view=view)
        script, div = components(p)
        return render(request, 'project/editplot.html', {'script': script, 'div':div, 'form':form, 'form2':form2, 'type':'Single', 'data':data,'currentplot':currentplot })

    if currentplot.plottype == 'Double':
        columns = ast.literal_eval(currentplot.columns)
        print(columns[0])
        source = ColumnDataSource(df)
        TOOLS = 'save,pan,box_zoom,reset,wheel_zoom'
        p = figure(
            title= currentplot.title,
            x_axis_type='datetime', 
            tools=TOOLS, 
            plot_height=400, 
            plot_width=700,
            )
        p.xaxis.axis_label = 'Time'
        # p.yaxis.axis_label = form.cleaned_data['Y']
        view = CDSView(source=source, filters=[])
        y = columns[0]
        y2 = columns[1]
        # p.multi_line(xs="xs", ys="ys", source=source, line_color="color",legend_group='group', view=view, line_width=2)
        line1 = p.line(x=df.columns.values[0], y=y, source=source, color=Spectral3[0], legend_label=y, view=view)
        line2 = p.line(x=df.columns.values[0], y=y2, source=source, color=Spectral3[2], legend_label=y2, view=view)
        line2 = p.line(x=df.columns.values[0], y=y, source=source, alpha = 0)
        hover = HoverTool(
            tooltips = [
                ('Date', f'@{dateindex}''{%F}'),
                (f"{y}", f"@{y}"),
                (f"{y2}", f"@{y2}"),
            ],
            formatters={
                f'@{dateindex}': 'datetime',
            },
            mode='vline',
            renderers=[line1]
        )
        p.add_tools(hover)
        script, div = components(p) 
        return render(request, 'project/editplot.html', {'script': script, 'div':div, 'form':form, 'form2':form2, 'type':'Double', 'data':data,'currentplot':currentplot})

    return render(request, 'project/editplot.html', {'form':form, 'form2':form2, 'data':data})


def plotList(request, pk):
    templates = 'project/plotlist.html'
    data = Dataset.objects.get(project=pk)
    plots = Plot.objects.filter(project=pk)
    print(data.project.id)
    return render(request, templates, {'plots': plots, 'projectid': pk, 'data':data})

def viewPlot(request, pk, plotpk):
    template = 'project/plotlist.html'
    #----------------------import data-------------------------#
    data = Dataset.objects.get(project=pk)
    title = data.title
    df = pd.read_csv(f'media/datasets/{title}')
    df.columns = df.columns.str.strip().str.replace(' ','_')
    df[df.columns[0]] = pd.to_datetime(df[df.columns[0]])
    dateindex = df.columns.values[0]
    print(df.Date.dtype)
    #------------------------------plotlist------------------------------------#
    plots = Plot.objects.filter(project=pk)
    #------------------------------viewplot------------------------------------#
    plot = Plot.objects.get(id=plotpk)

    if plot.plottype == 'Single':
        source = ColumnDataSource(df)
        print('singleline')
        TOOLS = 'save,pan,box_zoom,reset,wheel_zoom'
        p = figure(
            title= plot.title,
            x_axis_type='datetime', 
            tools=TOOLS, 
            plot_height=400, 
            plot_width=700,
            )
        p.xaxis.axis_label = 'Time'
        p.yaxis.axis_label = plot.columns
        view = CDSView(source=source, filters=[])
        hover = HoverTool(
            tooltips = [
                ('Date', f'@{dateindex}''{%F}'),
                (f"{plot.columns}", f"@{plot.columns}"),
            ],
            formatters={
                f'@{dateindex}': 'datetime',
            },
            mode='vline'
        )
        p.add_tools(hover)
        p.line(x=df.columns.values[0], y=plot.columns, source=source, view=view)
        script, div = components(p)
        return render(request, template, {'script': script, 'div':div, 'plots': plots, 'projectid': pk,'currentplot':plot, 'data':data})

    if plot.plottype == 'Double':
        #------------------------convert str to list----------------------#
        strcolumns = plot.columns
        listcolumns = strcolumns.strip("[]").replace("'","").replace(' ','').split(",")
        print(listcolumns)
        #-----------------------------------------------------------------#
        source = ColumnDataSource(df)
        TOOLS = 'save,pan,box_zoom,reset,wheel_zoom'
        p = figure(
            title= plot.title,
            x_axis_type='datetime', 
            tools=TOOLS, 
            plot_height=400, 
            plot_width=700,
            )
        p.xaxis.axis_label = 'Time'
        # p.yaxis.axis_label = form.cleaned_data['Y']
        view = CDSView(source=source, filters=[])
        y = listcolumns[0]
        y2 = listcolumns[1]
        # p.multi_line(xs="xs", ys="ys", source=source, line_color="color",legend_group='group', view=view, line_width=2)
        line1 = p.line(x=df.columns.values[0], y=y, source=source, color=Spectral3[0], legend_label=y, view=view)
        line2 = p.line(x=df.columns.values[0], y=y2, source=source, color=Spectral3[2], legend_label=y2, view=view)
        line2 = p.line(x=df.columns.values[0], y=y, source=source, alpha = 0)
        hover = HoverTool(
            tooltips = [
                ('Date', f'@{dateindex}''{%F}'),
                (f"{listcolumns[0]}", f"@{listcolumns[0]}"),
                (f"{listcolumns[1]}", f"@{listcolumns[1]}"),
            ],
            formatters={
                f'@{dateindex}': 'datetime',
            },
            mode='vline',
            renderers=[line1]
        )
        p.add_tools(hover)
        script, div = components(p)
    return render(request, template, {'script': script, 'div':div, 'plots': plots, 'projectid': pk, 'currentplot':plot, 'data':data})
    
def read_data(request, pk):
    templates = 'project/read.html'
    data = Dataset.objects.get(project=pk)
    title = data.title
    df = pd.read_csv(f'media/datasets/{title}')
    df.columns = df.columns.str.strip().str.replace(' ','_')
    df[df.columns[0]] = pd.to_datetime(df[df.columns[0]])

    pd.set_option('display.width', 1000)
    pd.set_option('colheader_justify', 'center')
    print(df.head())
    data_html = df.to_html(table_id='dtBasicExample', classes="table table-striped table-bordered")

    return render(request, templates, {'data': data_html, 'dataset': data})

def dashboard(request, pk):
    templates= 'project/dashboard.html'

    data = Dataset.objects.get(project=pk)
    title = data.title
    df = pd.read_csv(f'media/datasets/{title}')
    df.columns = df.columns.str.strip().str.replace(' ','_')
    df[df.columns[0]] = pd.to_datetime(df[df.columns[0]])
    dateindex = df.columns.values[0]
    plotdict = dict()
    plots = Plot.objects.filter(project=pk)
    for plot in plots:
        
        if plot.plottype == 'Single':
            source = ColumnDataSource(df)
            print('singleline')
            TOOLS = 'save,reset'
            p = figure(
                title= plot.title,
                x_axis_type='datetime', 
                tools=TOOLS, 
                plot_height=400, 
                plot_width=700,
                )
            p.xaxis.axis_label = 'Time'
            p.yaxis.axis_label = plot.columns
            view = CDSView(source=source, filters=[])
            hover = HoverTool(
                tooltips = [
                    ('Date', f'@{dateindex}''{%F}'),
                    (f"{plot.columns}", f"@{plot.columns}"),
                ],
                formatters={
                    f'@{dateindex}': 'datetime',
                },
                mode='vline'
            )
            p.add_tools(hover)
            p.line(x=df.columns.values[0], y=plot.columns, source=source, view=view)
            plotdict.update({f'{plot.title}' : p})

        if plot.plottype == 'Double':
            #------------------------convert str to list----------------------#
            strcolumns = plot.columns
            listcolumns = strcolumns.strip("[]").replace("'","").replace(' ','').split(",")
            print(listcolumns)
            #-----------------------------------------------------------------#
            source = ColumnDataSource(df)
            TOOLS = 'save,reset'
            p = figure(
                title= plot.title,
                x_axis_type='datetime', 
                tools=TOOLS, 
                plot_height=400, 
                plot_width=700,
                )
            p.xaxis.axis_label = 'Time'
            # p.yaxis.axis_label = form.cleaned_data['Y']
            view = CDSView(source=source, filters=[])
            y = listcolumns[0]
            y2 = listcolumns[1]
            # p.multi_line(xs="xs", ys="ys", source=source, line_color="color",legend_group='group', view=view, line_width=2)
            line1 = p.line(x=df.columns.values[0], y=y, source=source, color=Spectral3[0], legend_label=y, view=view)
            line2 = p.line(x=df.columns.values[0], y=y2, source=source, color=Spectral3[2], legend_label=y2, view=view)
            line2 = p.line(x=df.columns.values[0], y=y, source=source, alpha = 0)
            hover = HoverTool(
                tooltips = [
                    ('Date', f'@{dateindex}''{%F}'),
                    (f"{listcolumns[0]}", f"@{listcolumns[0]}"),
                    (f"{listcolumns[1]}", f"@{listcolumns[1]}"),
                ],
                formatters={
                    f'@{dateindex}': 'datetime',
                },
                mode='vline',
                renderers=[line1]
            )
            p.add_tools(hover)
            plotdict.update({f'{plot.title}' : p})

    script, div = components(plotdict)        
    return render(request, templates, {'plots': plots, 'script': script, 'div':div})

class projectDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Project
    success_url = '/list'

    def test_func(self):
        project = self.get_object()
        if self.request.user == project.author:
            return True
        return False


class plotDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Plot
    success_url = '/list'

    def test_func(self):
        plot = self.get_object()
        if self.request.user == plot.project.author:
            return True
        return False