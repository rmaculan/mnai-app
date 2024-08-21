from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required 
from django import forms
from .models import Item, UserMessage, Conversation, CategoryModel
import logging
from django.views.generic.edit import CreateView
from .forms import ItemPostForm
from django.core.files.storage import default_storage
from PIL import Image
from django.http import HttpResponseBadRequest
from django.db.models import Q


logger = logging.getLogger(__name__)

class ItemPostView(CreateView):
    model = Item
    form_class = ItemPostForm
    template_name = 'marketplace/item_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        if form.cleaned_data['image']:
            # Process the image here
            try:
                with default_storage.open(form.instance.image.name, 'rb+') as img_file:
                    img = Image.open(img_file)
                    img = img.resize((300, 300)) 
                    img.save(img_file)
            except IOError:
                pass  # Handle error
        return response
    
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # Redirect to a success page.
            return redirect('marketplace:index') 
    else:
        form = UserCreationForm()
    return render(request, 'marketplace/register.html', {'form': form})

def login_view(request):
        if request.method == 'POST':
            form = AuthenticationForm(data=request.POST)
            if form.is_valid():
                user = form.get_user()
                login(request, user)
                return redirect('marketplace:index')
        else:
            form = AuthenticationForm()
        return render(request, 'marketplace/login.html', {'form': form})

def logout_view(request):
    logger.info("Logout view accessed")
    logout(request)
    return redirect('marketplace:index')
        
def user_profile(request):
    user = request.user
    return render(request, 'marketplace/user_profile.html', {'user': user})

def index(request):
    newest_items = Item.objects.order_by('-id')[:5]
    context = {
        "newest_items": newest_items,
    }
    return render(request, "marketplace/index.html", context)

# Create
@login_required
def create_item(request):
    if request.method == 'POST':
        
        name = request.POST['name']
        description = request.POST['description']
        price = request.POST['price']
        quantity = request.POST.get('quantity', 1)  # Default to 1 if not provided
        image = request.FILES.get('image')

        logger.debug(f'Received files: {request.FILES}')

        # Convert category name to CategoryModel instance
        category_name = request.POST['category']
        category, created = CategoryModel.objects.get_or_create(name=category_name)

        # Use the currently logged-in user as the seller
        seller = request.user

        Item.objects.create(
            name=name, 
            description=description, 
            price=price, 
            quantity=quantity, 
            condition=request.POST['condition'],
            image=image,
            category=category,  # Now correctly assigns the CategoryModel instance
            seller=seller  # Assign the currently logged-in user as the seller
        )
        return redirect('marketplace:index')
    else:
        form = ItemPostForm()
        categories = CategoryModel.objects.all()  # Fetch all categories for selection
        return render(request, 'marketplace/item_form.html', {'form': form, 'categories': categories})
    
# Message seller
def contact_seller_form(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    
    if request.method == 'POST':
        message_text = request.POST['message']
        UserMessage.objects.create(
            item=item, 
            sender=request.user, 
            message=message_text, 
            receiver=item.seller
        )
        return redirect('marketplace:item_detail', item_id=item.id)
    
    # Handle GET request by rendering the form
    return render(request, 'marketplace/contact_seller_form.html', {'item': item})
    
# user messages
def user_messages(request):
    messages = UserMessage.objects.filter(receiver=request.user)
    return render(request, 'marketplace/messages.html', {'messages': messages})

# view conversation from all parties
def view_conversation(request, message_id):
    message = get_object_or_404(UserMessage, pk=message_id)
    # Adjusted to use Q objects for more flexible queries
    conversation = Conversation.objects.filter(
        Q(participants=message.sender) | Q(participants=message.receiver)
    )
    return render(request, 'marketplace/view_conversation.html', {'conversation': conversation, 'message': message})

# Reply to message
def reply_form(request, message_id):
    message = get_object_or_404(UserMessage, pk=message_id)
    if request.method == 'POST':
        message.message = request.POST['message']
        message.save()
        return redirect('marketplace:messages')
    else:
        return render(request, 'marketplace/reply_form.html', {'message': message})

# Read
def item_list(request):
    items = Item.objects.all().order_by('-id')
    return render(request, 'marketplace/index.html', {'items': items})

def item_detail(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    return render(request, 'marketplace/item_detail.html', {'item': item})

# view listed items by seller
def seller_items(request):
    items = Item.objects.filter(seller=request.user)
    return render(request, 'marketplace/seller_items.html', {'items': items})

def search_items(request):
    query = request.GET.get('query')
    items = Item.objects.filter(title__icontains=query)
    return render(request, 'marketplace/search_results.html', {'items': items})

@login_required
def update_item(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    if request.method == 'POST':
        form = ItemPostForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect('marketplace:item_detail', item_id=item.id)  # Redirect to detail view or another appropriate view
    else:
        form = ItemPostForm(instance=item)
    return render(request, 'marketplace/update_item.html', {'form': form})

# Delete
@login_required
def delete_item(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    if request.method == 'POST':
        item.delete()
        return redirect('marketplace:index')
    else:
        return render(request, 'marketplace/item_confirm_delete.html', {'item': item})


