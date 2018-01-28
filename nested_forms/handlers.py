'''Classes to ensure forms handle formsets as well'''

# a method named wrap_foo would be used by nest()
# to wrap a method named foo in form class.

class FormSetHandler:

    '''Wraps Form to make it operate in conjunction with FormSet.'''

    def __init__(self, formset_class, prefix):
        self.formset_class = formset_class
        self.prefix = prefix

    def wrap___init__(self, form_instance, *args, **kwargs):
        yield
        self.init_formset(form_instance)

    def wrap_is_valid(self, form_instance):
        '''Delegate is_valid() call to the child formsets in addition to doing
        the normal Django stuffs.'''
        form_valid = yield
        return form_valid and self.validate_formset(form_instance)

    def validate_formset(self, form_instance):
        '''Call is_valid() of formset instance'''
        return form_instance.formsets[self.prefix].is_valid()

    def get_formset_kwargs(self, form_instance): # pylint: disable=W0613, R0201
                                                 # suppress unused arg and method
                                                 # could be a function.
                                                 # subclasses might use these arguments.
        '''Return the dict of kwargs for instantiating a formset.'''
        return {}

    def init_formset(self, form_instance):
        '''instantiate self.formset_class'''
        try:
            formsets = form_instance.formsets
        except AttributeError:
            # it seems that self is the first handler to bind formset to
            # the form, so create dict to store formsets.
            formsets = form_instance.formsets = {}

        formset_instance = self.formset_class(
            data=form_instance.data if form_instance.is_bound else None,
            **self.get_formset_kwargs(form_instance)
        )

        # Prepend the prefix of our super form to the prefix of this
        # formset.
        # e.g. the super formset is prefixed as foo and our formset is
        # prefixed as bar, then the j th form of the formset bar nested
        # under the i th form of the formset foo is prefixed as
        # foo-i-bar-j
        formset_instance.prefix = form_instance.add_prefix(self.prefix)

        # store each formset instance in a dict,
        # mapping prefixes to instances
        formsets[self.prefix] = formset_instance

class ModelFormSetHandler(FormSetHandler):

    '''Wraps ModelForm to make it operate in conjunction with ModelFormSet.'''

    def wrap_save(self, form_instance, commit=True):
        '''Delegate save() call to the child formset in addition to doing
        the normal Django stuffs.'''
        saved_instance = yield
        self.save_formsets(form_instance, commit)
        return saved_instance

    def save_formsets(self, form_instance, commit):
        '''Call save() of each formset.'''
        form_instance.formsets[self.prefix].save(commit)


class InlineFormSetHandler(ModelFormSetHandler):

    '''Wraps ModelForm to make it operate in conjunction with InlineFormSet.'''

    def get_formset_kwargs(self, form_instance):
        '''Get a dict of kwargs for instantiating formsets.'''
        return {'instance': form_instance.instance}
