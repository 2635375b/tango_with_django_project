import os
#Sets up the settings.py file to be the settings file for this project. IMPORTANT!
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tango_with_django_project.settings')

import django
#Imports the Django project's settings
django.setup()
#Have to be imported after the above as the above help set up the necessary environment for these models to run
from rango.models import Category, Page

def populate():
    # First, we will create lists of dictionaries containing the pages
    # we want to add into each category.
    # Then we will create a dictionary of dictionaries for our categories.
    # This might seem a little bit confusing, but it allows us to iterate
    # through each data structure, and add the data to our models.

    python_pages = [
        {'title': 'Official Python Tutorial',
         'url':'http://docs.python.org/3/tutorial/'},
        {'title': 'How to Think like a Computer Scientist',
         'url': 'http://www.greenteapress.com/thinkpython/'},
        {'title': 'Learn Python in 10 Minutes',
         'url': 'http://www.korokithakis.net/tutorials/python/'}
    ]

    django_pages = [
        {'title': 'Official Django Tutorial',
         'url':'https://docs.djangoproject.com/en/2.1/intro/tutorial01/'},
        {'title': 'Django Rocks',
         'url': 'http://www.djangorocks.com/'},
        {'title': 'How to Tango with Django',
         'url': 'http://www.tangowithdjango.com/'}
    ]

    other_pages = [
        {'title':'Bottle',
         'url':'http://bottlepy.org/docs/dev/'},
        {'title':'Flask',
         'url':'http://flask.pocoo.org'},
    ]

    cats = {'Python':{'pages':python_pages, 'views': 128, 'likes': 64},
            'Django':{'pages':django_pages, 'views': 64, 'likes': 32},
            'Other Frameworks':{'pages':other_pages, 'views': 32, 'likes': 16}}

    # If you want to add more categories or pages,
    # add them to the dictionaries above.

    # The code below goes through the cats dictionary, then adds each category,
    # and then adds all the associated pages for that category.
    for cat, cat_data in cats.items():
        c = add_cat(cat, cat_data['views'], cat_data['likes'])
        for p in cat_data['pages']:
            add_page(c, p['title'], p['url'])

    #Print out the categories we have added.
    for c in Category.objects.all():
        for p in Page.objects.filter(category=c):
            print(f'- {c}: {p}')

def add_page(cat, title, url, views=0):
    #get_or_create checks if the entry already exists in the database or not; if it doesn't it creates it;
    #otherwise it returns a reference to the specific model instance required.
    #Returns a tuple (object, created) where created is a boolean value so [0] returns the object reference of the new/existing database entry
    p = Page.objects.get_or_create(category=cat, title=title)[0]
    p.url = url
    p.views = views
    p.save()
    return p

def add_cat(name, views=0, likes=0):
    c = Category.objects.get_or_create(name=name)[0]
    c.likes = likes
    c.views = views
    c.save()
    return c

#Start execution here!
#This if statement will only be executed if this module is run as a standalone Python script (either on the cmd or in the IDE)
#If this module is imported into another file in order to gain access to the functions this if statement won't be executed
if __name__ == '__main__':
    print('Starting Rango population script...')
    populate()



