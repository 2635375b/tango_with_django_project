from django.shortcuts import render, redirect
from django.http import HttpResponse
from tango_with_django_project import settings
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime

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

    visitor_cookie_handler(request)

    return render(request, 'rango/index.html', context=context_dict)

def about(request):
    visitor_cookie_handler(request)

    context_dict = {'visits': request.session['visits']}

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

@login_required
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
            return redirect(reverse('rango:index'))
        else:
            #The supplied form contained errors - just print them to the terminal
            print(form.errors)

    #Will handle the bad form, new form, or no form supplied cases.
    #Render the form with error messages (if any).
    return render(request, 'rango/add_category.html', {'form': form})

@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    if category is None:
        return redirect(reverse('rango:index'))

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

def register(request):
    #Boolean value for telling the template if the registration was successful
    #Set to false initially and changes to true when registration succeeds
    registered = False

    #If it's a HTTP POST, we're interested in processing form data
    if request.method == 'POST':
        #Attempt to grab info from the raw form info
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        #If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
            #Save the user's form data to the database
            user = user_form.save()

            #Hash the password with the set_password method
            #Once hashed the user object can be updated
            user.set_password(user.password)
            user.save()

            #Sort out the UserProfile instance, since we need to set the user attribute ourselves, set commit=False.
            #This delays saving the model until we're ready to avoid integrity problems
            profile = profile_form.save(commit=False)
            profile.user = user

            #Did the user provide a profile photo? If so, need to get it from the input form and put it in the UserProfile model
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            #Save the UserProfile model instance
            profile.save()

            #Update variable to indicate template registration success
            registered = True

    else:
        #Not a HTTP POST, so render form using two modelForm instances.
        #These forms will be blank, ready for user input
        user_form = UserForm()
        profile_form = UserProfileForm()

    #Render the template depending on the context
    return render(request, 'rango/register.html', context = {'user_form': user_form, 'profile_form': profile_form, 'registered': registered})

def user_login(request):
    if request.method == 'POST':
        #Gather the username and password provided by the user through the login form
        #Use request.POST.get('<variable>') as this will raise a KeyError if the value doesn't exist rather than returning None
        username = request.POST.get('username')
        password = request.POST.get('password')

        #Use Django's machinery to attempt to see of the username/password combination is valid.
        #A User object is returned if it is.
        user = authenticate(username=username, password=password)

        if user:
            #Checks if account is still active
            if user.is_active:
                #Log the user in as the account is valid and active.
                login(request, user)
                return redirect(reverse('rango:index'))
            else:
                return HttpResponse("Your Rango account is disabled.")
        else:
            #Bad login details provided
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")

    #Request isn't a HTTP POST so display the form
    else:
        return render(request, "rango/login.html")

@login_required
def restricted(request):
    return render(request, "rango/restricted.html")

@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('rango:index'))


def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)

    if not val:
        val = default_val

    return val

def visitor_cookie_handler(request):
    #Get the num of visits to the site.
    #COOKIES.get(0 func obtains the visits cookie.
    visits = int(get_server_side_cookie(request, 'visits', '1'))

    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')

    #If it's been more than a day since the last visit
    if (datetime.now() - last_visit_time).days > 0:
        visits += 1
        request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] = last_visit_cookie

    request.session['visits'] = visits
