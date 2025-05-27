from django.shortcuts import render
from django.http import JsonResponse
from .utils import get_roadmap_image_url

def generate_roadmap_image(request, project_id):
    """
    View to generate and return the roadmap image URL
    """
    try:
        image_url = get_roadmap_image_url(request, project_id)
        return JsonResponse({
            'success': True,
            'image_url': image_url
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
