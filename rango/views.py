from django.shortcuts import render, redirect
from django.http import HttpResponse
from tango_with_django_project import settings
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm
from django.urls import reverse

def index(request):
    #Query the database for a list of ALL categories currently stored.
    #Order the categories by the number of likes in descending order.
    #Retrieve the top 5 only -- or all if less than 5.
    #Place the list in our context_dict that will be passed to the template engine.
    #The - in -likes indicates to order in descending order
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    #Construct a dictionary to pass to the template engine as its context.
    #Note the key boldmessage matches to {{ boldmessage }} in the template!
    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = page_list

    #Return a rendered response to send to the client.
    #We make use of the shortcut function to make our lives easier.
    #Note that the first parameter is the template we wish to use.
    return render(request, 'rango/index.html', context = context_dict)

def about(request):
    context_dict = {'MEDIA_URL': settings.MEDIA_URL, 'boldmessage': 'This tutorial has been put together by Kirsty Balfour.'}

    return render(request, 'rango/about.html', context = context_dict)

def show_category(request, category_name_slug):
    #Create a context dictionary which we can pass to the template rendering engine
    context_dict = {}

    try:
        #Can we find a category name slug with the given name?
        #If we can't, the .get() method raises a DoesNotExist exception.
        #The .get() method returns one model instance or raises an exception.
        category = Category.objects.get(slug=category_name_slug)

        #Retrieve all of the associated pages.
        #The filter() will return a list of page objects or an empty list.
        pages = Page.objects.filter(category=category)

        #Adds our results list to the template context under name pages.
        context_dict['pages'] = pages
        #We also add the category objectg from the database to the context dictionary.
        #We'll use this in the template to verify that the category exists
        context_dict['category'] = category

    except Category.DoesNotExist:
        #We get here if we didn't find the specified category .
        #Don't do anything - the template will display the "no category" message for us
        context_dict['category'] = None
        context_dict['pages'] = None

    #Go render the response and return it to the client.
    return render(request, 'rango/category.html', context=context_dict)

def add_category(request):
    form = CategoryForm()

    #A HTTP POST? Did the user submit data via the form
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        #Have we been provided with a valid form?
        if form.is_valid():
            #Save the new category to the database
            form.save(commit=True)
            #Now that the category is saved, we could confirm this.
            #For now, just redirect the user back to the index view
            return redirect('/rango/')
        else:
            #The supplied form contained errors - just print them to the terminal
            print(form.errors)

    #Will handle the bad form, new form, or no form supplied cases.
    #Render the form with error messages (if any).
    return render(request, 'rango/add_category.html', {'form': form})

def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    if category is None:
        return redirect('/rango/')

    form = PageForm()

    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()

            return redirect(reverse('rango:show_category', kwargs={'category_name_slug': category_name_slug}))
        else:
            print(form.errors)

    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context=context_dict)

