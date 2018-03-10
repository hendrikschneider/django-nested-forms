Django nested forms
===================

A util to make Django formsets easy to use.


Overview
--------

Django provides powerful support for creating a complex app
with simple code, among which is support for creating a page with a
form for users to fill in. Although the framework provides a tool called
a formset, which is a collection of forms, to help build a page that has
multiple forms, working with formsets is a little bit more complex than
working with normal forms and requires some boilerplate code. This package
aims to help people use formsets with a minimum amount code and make formsets
even easier to use.


Usage
-----

Let's assume you have a model named Book and a model named Author. To allow
the user to edit several books at once, you use a decorator from this package
in your forms.py (or in your views.py if you do not have a separate module
for forms)::

    from django import forms
    from nested_forms import ModelFormSetHandler

    from .models import Author, Book

    BookFormSet = forms.modelformset_factory(
        model=Book,
        fields=['title', 'description']
    )

    @ModelFormSetHandler(
        BookFormSet, # specify the formset to include
        'book' # specify how we refer to the formset in our template later
    )
    class AuthorForm(forms.ModelForm):

        class Meta:
            model = Author
            fields = ['first_name', 'last_name']

You do not have to do nothing special in your views.py::

    from django.views.generic.edit import UpdateView

    from .models import Author
    from .forms import AuthorForm

    class UpdateAuthorView(UpdateView):

        model = Author
        form_class = AuthorForm
        template_name = 'author-form.html'

In your template access the book formset like this::

    <form method="POST" enctype="multipart/form-data">
        {% csrf_token %}
        {{ form.formsets.book }}
        {{ form }}
        <button type="submit">Submit</button>
    </form>

That's it. The decorator nested_forms.ModelFormSetHandler handles all the
complexity for you. All you have to do is to apply a decorator to a form
class, create your view just as usual, and display your formset as you like
in your template.


Installing
----------

Using pip::

    $ pip install git+https://github.com/ykiu/django-nested-forms


Tested with...
--------------

This package has been tested with

* Python 3.6
* Django 1.11


Misc
----

This package is still under development. The APIs may change in the future
and the code can contain a host of bugs (I'd be happy if you could send me a
bug report).


Contribution
------------
To controbute, fork the repo, do your work and make a pull request. Remember
to include tests for any new features or bug fixes. Your contribution
would be greatly appreciated:-)
