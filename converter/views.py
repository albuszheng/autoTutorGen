import json

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseRedirect

from .utl.file_handle import handle_uploaded_files
from .models import UploadFileForm, BehaviorGraph
from .brd.behavior_graph import build_behavior_graph, create_brd_file
from .brd.trace_analysis import get_cognitive_model, var_analysis
from .utl.db_trace import get_code_trace

# Create your views here.

def index(request):
    return render(request, 'preview.html', {'var_list': ['i','x'], 'code': 'x = 1\nfor i in range(1, 2):\n    x += i', 'name': "addSum", 'var_num': 3})


def welcome(request):
    return render(request, 'index.html')


def about(request):
    # return HttpResponse("this is the base.html page, detailing the process")
    return render(request, 'about.html')


def processing(request):
    if 'behavior_model' not in request.session:
        return HttpResponseRedirect('/convert/upload')

    behavior_model_id = request.session.get('behavior_model')
    behavior_model = get_object_or_404(BehaviorGraph, pk=behavior_model_id)

    json_dec = json.decoder.JSONDecoder()
    print(json_dec.decode(behavior_model.trace))
    print(json_dec.decode(behavior_model.var_list))
    cognitive_model, variables = get_cognitive_model(json_dec.decode(behavior_model.var_list), json_dec.decode(behavior_model.trace))
    brd = build_behavior_graph(cognitive_model, behavior_model.problem_name if behavior_model.problem_name is not None else behavior_model.name, json_dec.decode(behavior_model.var_list))

    behavior_model.cog_model = json.dumps(cognitive_model)
    behavior_model.brd = json.dumps(brd)

    behavior_model.save()

    return HttpResponseRedirect('/converter/result/' + str(behavior_model.id))


def result(request, behavior_model_id):
    if 'behavior_model' not in request.session:
        return HttpResponseRedirect('/convert/upload')

    # behavior_model_id = request.session.get('behavior_model')
    behavior_model = get_object_or_404(BehaviorGraph, pk=behavior_model_id)

    model = {'name': behavior_model.name,
             'problem_name': behavior_model.problem_name,
             'code': behavior_model.code,
             'id': behavior_model.id,
             'preview': '/converter/preview/'+str(behavior_model_id),
             'brd': '/converter/brd/'+str(behavior_model_id)}

    return render(request, 'result.html', {'model': model})


def brd_download(request, behavior_model_id):
    # if 'files' not in request.session:
    #     return HttpResponseRedirect('/convert/upload')

    behavior_model = get_object_or_404(BehaviorGraph, pk=behavior_model_id)

    json_dec = json.decoder.JSONDecoder()

    response = HttpResponse(json_dec.decode(behavior_model.brd), content_type='application/brd')
    response['Content-Disposition'] = 'attachment; filename=' + behavior_model.problem_name + '_brd.brd'
    return response
    # return HttpResponse("this is the page showing the converting result")


def preview(request, behavior_model_id):
    json_dec = json.decoder.JSONDecoder()

    behavior_model = get_object_or_404(BehaviorGraph, pk=behavior_model_id)
    var_list = json_dec.decode(behavior_model.var_list)
    code = behavior_model.code
    name = behavior_model.problem_name if behavior_model.problem_name is not None else behavior_model.name

    # if 'files' not in request.session:
    #     return HttpResponseRedirect('/convert/upload')
    return render(request, 'preview.html', {'var_list': var_list, 'code': code, 'name': name, 'url': '/converter/brd/'+str(behavior_model_id), 'var_num': str(len(var_list) + 1), 'steps': len(json_dec.decode(behavior_model.cog_model))})


def upload_success(request):
    if 'behavior_model' not in request.session:
        print('No sessions')
        return HttpResponseRedirect('/converter/upload')

    behavior_models = request.session.get('behavior_models')

    if len(behavior_models) == 0:
        print('No Models')
        return HttpResponseRedirect('/converter/upload')

    waiting_config = []

    for behavior_model_id in behavior_models:
        behavior_model = BehaviorGraph.objects.get(pk=behavior_model_id)
        waiting_config.append({'id': behavior_model_id, 'name': behavior_model.name, 'code': behavior_model.code, 'var_list': behavior_model.var_list})

    return render(request, 'brd_config.html', {'waiting_config': waiting_config})


def upload_fail(request):
    if 'files' not in request.session:
        return HttpResponseRedirect('/convert/upload')
    return HttpResponse("this is the page when the upload is unsuccessful")


def upload(request):
    return render(request, 'input.html')


def upload_file(request):
    print(request.session)
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        # print(form.is_valid())
        # if form.is_valid():
        files = handle_uploaded_files(request.FILES)
        behavior_model_list = []

        for file in files:
            behavior_model = BehaviorGraph()
            behavior_model.name = file['name']
            behavior_model.problem_name = file['name'].split('.')[0]
            behavior_model.code = file['content']
            behavior_model.trace = json.dumps(file['trace'])
            behavior_model.var_list = json.dumps(file['variable_list'])
            behavior_model.save()
            print(behavior_model)
            behavior_model_list.append(behavior_model.id)

        request.session['behavior_model'] = behavior_model_list[0]
        # return render(request, 'brd_config.html')
        return HttpResponseRedirect('/converter/processing')
    else:
        form = UploadFileForm()
    return render(request, 'input.html')


def code_submitting(request):
    if request.method == 'POST':
        behavior_model = BehaviorGraph()
        behavior_model.name = request.POST['code_name']
        behavior_model.code = request.POST['code']
        behavior_model.problem_name = behavior_model.name
        trace = get_code_trace(behavior_model.code, False)
        behavior_model.trace = json.dumps(trace)
        var_list = var_analysis(trace)
        behavior_model.var_list = json.dumps(var_list)

        behavior_model.save()
        request.session['behavior_model'] = behavior_model.id
        return HttpResponseRedirect('/converter/processing')
    else:
        return HttpResponseRedirect('/converter/upload')


def config_submit(request, behavior_model_id):
    behavior_model = get_object_or_404(BehaviorGraph, pk=behavior_model_id)
    if request.method == 'POST':
        behavior_model.problem_name = request.POST['problem_name']

        behavior_model.save()

        request.session['behavior_model'] = behavior_model_id

        return render(request, 'processing.html')
    else:
        render(request, 'brd_config.html', {'waiting_config': [{'id': behavior_model_id, 'name': behavior_model.name, 'code': behavior_model.code,
                               'var_list': behavior_model.var_list}]})



