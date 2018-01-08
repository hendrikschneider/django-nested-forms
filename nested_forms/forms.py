'''Mixins for nesting formsets in forms.'''

from django.db import transaction

class NestMixin:

    '''A mixin to nest formsets in a form.

    Takes care of formset instantiation and validation.'''

    # Map prefixes to formset classes.
    formset_classes = {}
    # As in normal Django formsets, prefix is used to namespace fields in
    # different forms. Here we use prefix as an identifier of each formset.
    # Subclasses should override formset_classes to register formsets to nest.

    def __init__(self, *args, **kwargs):
        super(NestMixin, self).__init__(*args, **kwargs)

        # Mapping prefixes to formset instances.
        self.formsets = {}

        self._init_formsets()

    def __repr__(self):
        if self._errors is None:
            is_valid = "Unknown"
        else:
            try:
                formset_valid = self.validate_formsets()
            except: # pylint: disable=W0702
                # __repr__ should not raise any exception for convinience.
                is_valid = "Unknown"
            else:
                is_valid = self.is_bound and not bool(self._errors) and formset_valid
        return '<%(cls)s bound=%(bound)s, valid=%(valid)s, fields=(%(fields)s)>' % {
            'cls': self.__class__.__name__,
            'bound': self.is_bound,
            'valid': is_valid,
            'fields': ';'.join(self.fields),
        }

    def is_valid(self):
        '''Delegate is_valid() call to the child formsets in addition to doing
        the normal Django stuff.'''
        formsets_valid = self.validate_formsets()
        self_valid = super(NestMixin, self).is_valid()
        return formsets_valid and self_valid

    def validate_formsets(self, formsets=None):
        '''Call is_valid() of each formset.

        Return True if all the formsets are valid, and False the otherwise.'''
        return all(formset.is_valid() for formset in (formsets or self.formsets).values())

    def get_formset_kwargs(self, prefix): # pylint: disable=W0613, R0201
                                          # suppress unused arg and method
                                          # could be a function.
                                          # subclasses might use the arguments.
        '''Get a dict of kwargs for instantiating formsets.

        Users may override this method in a subclass to pass arbitrary
        parameters to formset instances.'''
        return {}

    def _init_formsets(self, formset_classes=None, formsets=None):
        '''instantiate every formset class'''
        formsets = formsets if formsets is not None else self.formsets
        for prefix, formset in (formset_classes or self.formset_classes).items():
            formset_instance = formset(
                data=self.data if self.is_bound else None,
                **self.get_formset_kwargs(prefix)
            )

            # prepend the superform-prefix to the subform-prefix
            # to prevent name collision between formsets
            formset_instance.prefix = self.add_prefix(prefix)

            # store each formset instance in a dict,
            # mapping prefixes to instances
            formsets[prefix] = formset_instance


class ModelNestMixin(NestMixin):

    '''A mixin to nest model formsets in a model form.

    Takes care of model saving as well as
    formset instantiation and validation.'''

    def save(self, commit=True):
        '''Delegate save() call to the child formsets in addition to doing
        the normal Django stuffs.'''
        saved_instance = None
        with transaction.atomic():
            saved_instance = super(ModelNestMixin, self).save(commit)
            self.save_formsets(commit)

        return saved_instance

    def save_formsets(self, commit, formsets=None):
        '''Call save() of each formset.'''
        for formset in (formsets or self.formsets).values():
            formset.save(commit)

class InlineNestMixin(ModelNestMixin):

    '''A mixin to nest inline formsets in a model form

    Takes care of model saving as well as
    formset instantiation and validation.'''

    def get_formset_kwargs(self, prefix):
        '''Get a dict of kwargs for instantiating formsets.

        Users may override this method in a subclass to pass arbitrary
        parameters to formset instances.'''
        return {'instance': self.instance}
