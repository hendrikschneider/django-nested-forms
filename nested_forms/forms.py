'''Mixin factories for nesting formsets in forms.'''

from django.db import transaction
from .mixin_factory import MixinFactory

class NestedFormsets(MixinFactory):

    '''Create a mixin to nest formsets in a form.

    The resulting mixin takes care of formset instantiation and validation.'''

    def __init__(self, **formset_classes):
        # Map prefixes to formset classes.
        self.formset_classes = formset_classes
        # As in normal Django formsets, prefix is used to namespace fields in
        # different forms. Here we use prefix as an identifier of each formset.
        # Subclasses should override formset_classes to register formsets to nest.

    def create___init__(self):
        def __init__(mixin_instance, *args, **kwargs):
            super(self.mixin_class, mixin_instance).__init__(*args, **kwargs)
            self.init_formsets(mixin_instance)
        return __init__

    def create___repr__(self):
        def __repr__(mixin_instance):
            if mixin_instance._errors is None:
                is_valid = "Unknown"
            else:
                try:
                    formset_valid = mixin_instance.validate_formsets()
                except: # pylint: disable=W0702
                    # __repr__ should not raise any exception for convinience.
                    is_valid = "Unknown"
                else:
                    is_valid = mixin_instance.is_bound and not bool(mixin_instance._errors) and formset_valid
            return '<%(cls)s bound=%(bound)s, valid=%(valid)s, fields=(%(fields)s)>' % {
                'cls': mixin_instance.__class__.__name__,
                'bound': mixin_instance.is_bound,
                'valid': is_valid,
                'fields': ';'.join(mixin_instance.fields),
            }
        return __repr__

    def create_is_valid(self):
        def is_valid(mixin_instance):
            '''Delegate is_valid() call to the child formsets in addition to doing
            the normal Django stuff.'''
            formsets_valid = self.validate_formsets(mixin_instance)
            self_valid = super(self.mixin_class, mixin_instance).is_valid()
            return formsets_valid and self_valid
        return is_valid

    def validate_formsets(self, mixin_instance):
        '''Call is_valid() of each formset.

        Return True if all the formsets are valid, and False the otherwise.'''
        return all(formset.is_valid() for prefix, formset in mixin_instance.formsets.items()
                                      if prefix in self.formset_classes)

    def get_formset_kwargs(self, mixin_instance): # pylint: disable=W0613, R0201
                                        # suppress unused arg and method
                                        # could be a function.
                                        # subclasses might use the arguments.
        '''Get a dict of kwargs for instantiating formsets.'''
        return {}

    def init_formsets(self, mixin_instance):
        '''instantiate every formset class'''
        try:
            formsets = mixin_instance.formsets
        except AttributeError:
            formsets = mixin_instance.formsets = {}

        for prefix, formset in self.formset_classes.items():
            formset_instance = formset(
                data=mixin_instance.data if mixin_instance.is_bound else None,
                **self.get_formset_kwargs(mixin_instance)
            )

            # prepend the superform-prefix to the subform-prefix
            # to prevent name collision between formsets
            formset_instance.prefix = mixin_instance.add_prefix(prefix)

            # store each formset instance in a dict,
            # mapping prefixes to instances
            formsets[prefix] = formset_instance

class NestedModelFormsets(NestedFormsets):

    '''Create a mixin to nest model formsets in a model form.

    The resulting mixin takes care of model saving as well as
    formset instantiation and validation.'''

    def create_save(self):
        def save(mixin_instance, commit=True):
            '''Delegate save() call to the child formsets in addition to doing
            the normal Django stuffs.'''
            saved_instance = None
            with transaction.atomic():
                saved_instance = super(self.mixin_class, mixin_instance).save(commit)
                self.save_formsets(mixin_instance, commit)

            return saved_instance
        return save

    def save_formsets(self, mixin_instance, commit):
        '''Call save() of each formset.'''
        for prefix, formset in mixin_instance.formsets.items():
            if prefix not in self.formset_classes:
                continue
            formset.save(commit)


class NestedInlineFormsets(NestedModelFormsets):

    '''Create a mixin to nest inline formsets in a model form.

    The resulting mixin takes care of model saving as well as
    formset instantiation and validation.'''

    def get_formset_kwargs(self, mixin_instance):
        '''Get a dict of kwargs for instantiating formsets.'''
        return {'instance': mixin_instance.instance}
