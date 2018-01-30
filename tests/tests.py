'''Tests mixin factories.'''

from django import forms
from django.test import TestCase

from nested_forms import FormSetHandler, ModelFormSetHandler, InlineFormSetHandler

from tests.models import SampleChildModel, SampleRelatedModel, SampleParentModel

# Suppress warnings for dynamic attributes
# pylint:disable=E1101

class SampleChildForm(forms.Form):

    sample_field = forms.CharField(max_length=8)


class FormSetHandlerTest(TestCase):

    '''Test cases for FormSetHandler and its subclasses'''

    FormsetClass = forms.formset_factory(SampleChildForm)

    @FormSetHandler(FormsetClass, 'child')
    class ParentFormClass(forms.Form):
        sample_field = forms.CharField(max_length=8)


    def test_init_without_data(self):
        '''Child formsets are init()ed as their parents are init()ed.'''
        parent = self.ParentFormClass()
        child = parent.formsets.get('child')
        self.assertIsInstance(child, self.FormsetClass)

    def test_init_with_data(self):
        data = {
            'sample_field': 'spam',
            'child-TOTAL_FORMS': 1,
            'child-INITIAL_FORMS': 0,
            'child-MIN_NUM_FORMS': 0,
            'child-MAX_NUM_FORMS': 1000,
            'child-0-sample_field': 'eggs',
        }
        parent = self.ParentFormClass(data)
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
        parent = self.ParentFormClass(data)
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
        parent = self.ParentFormClass(data)
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
        parent = self.ParentFormClass(data)
        child = parent.formsets['child']
        self.assertFalse(parent.is_valid())

    def test_prefix(self):
        '''Fields in child formsets have prefix'''
        parentA = self.ParentFormClass()
        childA = parentA.formsets.get('child')
        self.assertEqual(childA[0].prefix, 'child-0')

        parentB = self.ParentFormClass(prefix='parent')
        childB = parentB.formsets.get('child')
        self.assertEqual(childB[0].prefix, 'parent-child-0')


class ModelFormSetHandlerTest(FormSetHandlerTest):

    '''Test cases for ModelFormSetHandler and its subclasses'''

    FormsetClass = forms.modelformset_factory(
        model=SampleChildModel,
        fields=['sample_field']
    )

    @ModelFormSetHandler(FormsetClass, 'child')
    class ParentFormClass(forms.ModelForm):

        class Meta:
            model = SampleParentModel
            fields = ['sample_field']


    def test_save(self):
        '''Models for both parent and child forms are created.'''
        parent_model_class = self.ParentFormClass._meta.model
        child_model_class = self.FormsetClass.model

        data = {
            'sample_field': 'spam',
            'child-TOTAL_FORMS': 1,
            'child-INITIAL_FORMS': 0,
            'child-MIN_NUM_FORMS': 0,
            'child-MAX_NUM_FORMS': 1000,
            'child-0-sample_field': 'eggs',
        }
        parent = self.ParentFormClass(data)
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

class InlineFormSetHandlerTest(ModelFormSetHandlerTest):

    '''Test cases for InlineFormSetHandler.'''


    FormsetClass = forms.inlineformset_factory(
        parent_model=SampleParentModel,
        model=SampleRelatedModel,
        fields=['sample_field']
    )

    @InlineFormSetHandler(FormsetClass, 'child')
    class ParentFormClass(forms.ModelForm):

        class Meta:
            model = SampleParentModel
            fields = ['sample_field']


    def test_relation(self):
        '''Child model instances are created with the reference to the parents.'''
        parent_model_class = self.ParentFormClass._meta.model
        child_model_class = self.FormsetClass.model

        data = {
            'sample_field': 'spam',
            'child-TOTAL_FORMS': 1,
            'child-INITIAL_FORMS': 0,
            'child-MIN_NUM_FORMS': 0,
            'child-MAX_NUM_FORMS': 1000,
            'child-0-sample_field': 'eggs',
        }
        parent = self.ParentFormClass(data)
        parent.is_valid()
        parent.save()

        self.assertEqual(child_model_class.objects.get(pk=1).parent_id, 1)
