from django.shortcuts import render, redirect

from category.models import Category



# Category Block/Unblock
def category_action(request, category_id):
    category = Category.objects.get(id=category_id)
    
    if category.is_available:
        category.is_available = False
    else:
        category.is_available = True
        
    category.save()
    
    return redirect('admin_techify:category_management')


# Add Category
def add_category(request):
    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        category_img = request.FILES.get('category_image')
        
        add_category = Category.objects.create(name=category_name, image=category_img)
        add_category.save()
        
        return redirect('admin_techify:category_management')
    return render(request, 'admin/add_category.html')


# Edit Category
def edit_category(request, category_id):
    edit_category = Category.objects.get(id=category_id)
    
    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        category_img = request.FILES.get('category_image')
        
        edit_category.name = category_name
        if category_img:
            edit_category.image = category_img
        edit_category.save()
            
        return redirect('admin_techify:category_management')
    return render(request, 'admin/edit_category.html', {'edit_category': edit_category})


    