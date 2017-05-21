from django.shortcuts import redirect

from marketplace.models import Category, Package

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
        object_to_like.recount_recommendations()
    return redirect(to=object_to_like.get_absolute_url())


def get_recommendations(step):
    relevant_category = Category.objects.filter(name__icontains=step.step.name)
    if relevant_category:
        relevant_category = relevant_category[0]
        recommended_packages = Package.objects.filter(category=relevant_category,
                                                      recommended__gte=1).order_by('recommended')[:5]
        return list(recommended_packages)
    return []
