import json

from django.http import JsonResponse

from core_app.models import Model, Part

from django.http import HttpResponse, Http404
from django.contrib.admin.views.decorators import staff_member_required
import os


def fetch_data_by_brand_or_part_group(request):
    request_data = json.loads(request.body)
    key = list(request_data.keys())[0]
    if 'brand_id' == key:
        brand_id = request_data[key]
        if brand_id == '':
            return JsonResponse({'data': '----'})
        model = Model.objects.filter(brand=brand_id)
        model_ids = extract_ids(model)
        return JsonResponse({'data': model_ids})

    if 'part_group_id' == key:
        part_group_id = request_data[key]
        if part_group_id == '':
            return JsonResponse({'data': '----'})
        part = Part.objects.filter(part_group=part_group_id)
        part_ids = extract_ids(part)
        return JsonResponse({'data': part_ids})


def extract_ids(data):
    ids = ['']
    for query in data:
        ids.append(query.id)
    return ids


@staff_member_required
def download_file(request, file_pk):
    from .models import ExportedFile  # Ensure you import your model here

    try:
        exported_file = ExportedFile.objects.get(pk=file_pk)
        file_path = exported_file.filepath

        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type="application/octet-stream")
                response['Content-Disposition'] = f'attachment; filename={os.path.basename(file_path)}'
                return response
        else:
            raise Http404("File does not exist")

    except ExportedFile.DoesNotExist:
        raise Http404("File does not exist")
