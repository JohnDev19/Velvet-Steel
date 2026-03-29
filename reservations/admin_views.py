"""
Patch for admin_views.py — replace only the two haircut-style view functions.
The rest of admin_views.py remains unchanged.
"""

@admin_required
def admin_haircut_style_add(request):
    from .forms import HaircutStyleForm
    if request.method == 'POST':
        form = HaircutStyleForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data.copy()
            image_file = data.pop('image', None)

            style = HaircutStyle(**data)

            if image_file:
                import os
                from django.conf import settings
                upload_dir = os.path.join(settings.MEDIA_ROOT, 'haircut_styles')
                os.makedirs(upload_dir, exist_ok=True)
                filename = f"{style.name.lower().replace(' ', '_')}_{image_file.name}"
                filepath = os.path.join(upload_dir, filename)
                with open(filepath, 'wb+') as dest:
                    for chunk in image_file.chunks():
                        dest.write(chunk)
                style.image = f"haircut_styles/{filename}"

            style.save()
            messages.success(request, 'Haircut style added successfully.')
            return redirect('admin_haircut_styles')
    else:
        form = HaircutStyleForm()
    return render(request, 'admin_panel/haircut_style_form.html', {'form': form, 'action': 'Add'})


@admin_required
def admin_haircut_style_edit(request, pk):
    from .forms import HaircutStyleForm
    style = HaircutStyle.objects(id=pk).first()
    if not style:
        messages.error(request, 'Style not found.')
        return redirect('admin_haircut_styles')
    if request.method == 'POST':
        form = HaircutStyleForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data.copy()
            image_file = data.pop('image', None)

            for k, v in data.items():
                setattr(style, k, v)

            if image_file:
                import os
                from django.conf import settings
                upload_dir = os.path.join(settings.MEDIA_ROOT, 'haircut_styles')
                os.makedirs(upload_dir, exist_ok=True)
                filename = f"{style.name.lower().replace(' ', '_')}_{image_file.name}"
                filepath = os.path.join(upload_dir, filename)
                with open(filepath, 'wb+') as dest:
                    for chunk in image_file.chunks():
                        dest.write(chunk)
                style.image = f"haircut_styles/{filename}"

            style.save()
            messages.success(request, f'"{style.name}" updated successfully.')
            return redirect('admin_haircut_styles')
    else:
        form = HaircutStyleForm(initial={
            'name':        style.name,
            'category':    style.category,
            'description': style.description,
            'price':       style.price,
            'is_active':   style.is_active,
        })
    return render(request, 'admin_panel/haircut_style_form.html', {
        'form': form, 'action': 'Edit', 'style': style
    })