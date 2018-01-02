'''Tests mixins.'''

from django import forms
from django.test import TestCase

from nested_forms.forms import NestMixin, ModelNestMixin, InlineNestMixin

from tests.models import SampleChildModel, SampleRelatedModel, SampleParentModel

# Form and form sets
class SampleChildForm(forms.Form):
    sample_field = forms.CharField(max_length=8)

SampleChildFormSet = forms.formset_factory(SampleChildForm)

class SampleParentForm(NestMixin,
                       forms.Form):

    formset_classes = {'child': SampleChildFormSet}
    sample_field = forms.CharField(max_length=8)

SampleModelChildFormSet = forms.modelformset_factory(
    model=SampleChildModel,
    fields=['sample_field']
)

class SampleModelParentForm(ModelNestMixin,
                            forms.ModelForm):

    formset_classes = {'child': SampleModelChildFormSet}

    class Meta:
        model = SampleParentModel
        fields = ['sample_field']

SampleInlineChildFormSet = forms.inlineformset_factory(
    parent_model=SampleParentModel,
    model=SampleRelatedModel,
    fields=['sample_field']
)

class SampleInlineParentForm(InlineNestMixin,
                            forms.ModelForm):

    formset_classes = {'child': SampleInlineChildFormSet}

    class Meta:
        model = SampleParentModel
        fields = ['sample_field']


class BaseMixinTest(TestCase):

    '''Test cases for NestMixin and its subclasses'''

    parent_form_class = SampleParentForm
    formset_class = SampleChildFormSet

    def test_init_without_data(self):
        '''Child formsets are init()ed as their parents are init()ed.'''
        parent = self.parent_form_class()
        child = parent.formsets.get('child')
        self.assertIsInstance(child, self.formset_class)

    def test_init_with_data(self):
        data = {
            'sample_field': 'spam',
            'child-TOTAL_FORMS': 1,
            'child-INITIAL_FORMS': 0,
            'child-MIN_NUM_FORMS': 0,
            'child-MAX_NUM_FORMS': 1000,
            'child-0-sample_field': 'eggs',
        }
        parent = self.parent_form_class(data)
        child = parent.formsets['child']

        self.assertEqual(parent['sample_field'].data, 'spam')
        self.assertEqual(child[0]['sample_field'].data, 'eggs')

    def test_is_valid_normal(self):
        data = {
            'sample_field': 'spam',
            'child-TOTAL_FORMS': 1,
            'child-INITIAL_FORMS': 0,
            'child-MIN_NUM_FORMS': 0,
            'child-MAX_NUM_FORMS': 1000,
            'child-0-sample_field': 'eggs',
        }
        parent = self.parent_form_class(data)
        child = parent.formsets['child']

        self.assertTrue(parent.is_valid())


    def test_is_valid_parent_invalid(self):
        data = {
            'sample_field': 'This string exceeds the max length for this field.',
            'child-TOTAL_FORMS': 1,
            'child-INITIAL_FORMS': 0,
            'child-MIN_NUM_FORMS': 0,
            'child-MAX_NUM_FORMS': 1000,
            'child-0-sample_field': 'eggs',
        }
        parent = self.parent_form_class(data)
        child = parent.formsets['child']

        self.assertFalse(parent.is_valid())

    def test_is_valid_child_invalid(self):
        data = {
            'sample_field': 'spam',
            'child-TOTAL_FORMS': 1,
            'child-INITIAL_FORMS': 0,
            'child-MIN_NUM_FORMS': 0,
            'child-MAX_NUM_FORMS': 1000,
            'child-0-sample_field': 'This string exceeds the max length for this field.',
        }
        parent = self.parent_form_class(data)
        child = parent.formsets['child']
        self.assertFalse(parent.is_valid())

    def test_prefix(self):
        '''Fields in child formsets have prefix'''
        parentA = self.parent_form_class()
        childA = parentA.formsets.get('child')
        self.assertEqual(childA[0].prefix, 'child-0')

        parentB = self.parent_form_class(prefix='parent')
        childB = parentB.formsets.get('child')
        self.assertEqual(childB[0].prefix, 'parent-child-0')


class ModelMixinTest(BaseMixinTest):

    '''Test cases for ModelMixin.'''

    parent_form_class = SampleModelParentForm
    formset_class = SampleModelChildFormSet

    def test_save(self):
        '''Models for both parent and child forms are created.'''
        parent_model_class = self.parent_form_class._meta.model
        child_model_class = self.formset_class.model

        data = {
            'sample_field': 'spam',
            'child-TOTAL_FORMS': 1,
            'child-INITIAL_FORMS': 0,
            'child-MIN_NUM_FORMS': 0,
            'child-MAX_NUM_FORMS': 1000,
            'child-0-sample_field': 'eggs',
        }
        parent = self.parent_form_class(data)
        parent.is_valid()
        parent.save()

        self.assertEqual(parent_model_class.objects.count(), 1)
        self.assertEqual(child_model_class.objects.count(), 1)

        self.assertEqual(
            parent_model_class.objects.get(pk=1).sample_field,
            'spam'
        )
        self.assertEqual(
            child_model_class.objects.get(pk=1).sample_field,
            'eggs'
        )

class InlineMixinTest(ModelMixinTest):

    '''Test cases for InlineMixin.'''

    parent_form_class = SampleInlineParentForm
    formset_class = SampleInlineChildFormSet

    def test_relation(self):
        '''Child model instances are created with the reference to the parents.'''
        parent_model_class = self.parent_form_class._meta.model
        child_model_class = self.formset_class.model

        data = {
            'sample_field': 'spam',
            'child-TOTAL_FORMS': 1,
            'child-INITIAL_FORMS': 0,
            'child-MIN_NUM_FORMS': 0,
            'child-MAX_NUM_FORMS': 1000,
            'child-0-sample_field': 'eggs',
        }
        parent = self.parent_form_class(data)
        parent.is_valid()
        parent.save()

        self.assertEqual(child_model_class.objects.get(pk=1).parent_id, 1)
