from django.shortcuts import render, redirect
from . models import Category
# Create your views here.

def category_action(request, id):
    category = Category.objects.get(id=id)
    if category.is_available:
        category.is_available = False
    else:
        category.is_available = True
        
    category.save()
    return redirect('admin_techify:category')