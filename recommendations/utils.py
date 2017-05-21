from django.shortcuts import redirect

from .models import Recommendation


def recommend(object_to_like, workbench_user):
    existing_recommendation = object_to_like.recommendations.filter(liked_by=workbench_user)
    if existing_recommendation:
        existing_recommendation = existing_recommendation[0]
        existing_recommendation.delete()
    else:
        recommendation = Recommendation()
        recommendation.content_object = object_to_like
        recommendation.liked_by = workbench_user
        recommendation.save()
    return redirect(to=object_to_like.get_absolute_url())
