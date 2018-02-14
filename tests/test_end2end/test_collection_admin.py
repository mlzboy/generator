import os

import pytest


@pytest.mark.django_gen('sample', """

#car
-------
nr
mark
model
weight: int
crashed: bool(true)
painted: bool

@admin {list: *}

""")
@pytest.mark.django_gen_before('install', 'migrate')
def test_admin_simple():
    from sample.admin import CarAdmin
    from django.contrib.admin import ModelAdmin

    assert issubclass(CarAdmin, ModelAdmin)

    assert CarAdmin.list_display == ['nr', 'mark', 'model', 'weight', 'crashed', 'painted']


@pytest.mark.django_gen_before('install', 'migrate')
@pytest.mark.django_gen('sample', """
#car
-------
nr
mark
model
weight: int
crashed: bool(true)
painted: bool

@admin {
    list: *, ^crashed
    list_editable: painted
    list_filter: mark, model
    list_search: nr
    
    tabs: main(*, ^weight), options(crashed, painted)
}

""")
def test_admin_more_options():
    from sample.admin import CarAdmin
    from django.contrib.admin import ModelAdmin

    assert issubclass(CarAdmin, ModelAdmin)

    assert CarAdmin.list_display == ['nr', 'mark', 'model', 'weight', 'painted']
    assert CarAdmin.list_editable == ['painted']
    assert CarAdmin.list_filter == ['mark', 'model']
    assert CarAdmin.search_fields == ['nr']

    assert CarAdmin.suit_form_tabs == (
        ('general', 'General'),  # this is always here
        ('main', 'Main'),
        ('options', 'Options'),
    )

    assert CarAdmin.fieldsets == (
        (None, {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': ['weight']
        }),
        (None, {
            'classes': ('suit-tab', 'suit-tab-main',),
            'fields': ['nr', 'mark', 'model']
        }),
        (None, {
            'classes': ('suit-tab', 'suit-tab-options',),
            'fields': ['crashed', 'painted']
        }),)


@pytest.mark.skip
@pytest.mark.django_gen_before('install', 'migrate')
@pytest.mark.django_gen('sample', """
#car
-------
nr
mark
model
weight: int
crashed: bool(true)
painted: bool

@admin {
    fields: *, ^weight
    tabs: main(*), options(crashed, painted)
}

""")
def test_admin_more_options_no_weight():
    from sample.admin import CarAdmin
    from django.contrib.admin import ModelAdmin

    assert CarAdmin.suit_form_tabs == (
        ('main', 'Main'),
        ('options', 'Options'),
    )

    assert CarAdmin.fieldsets == (
        (None, {
            'classes': ('suit-tab', 'suit-tab-main',),
            'fields': ['nr', 'mark', 'model']
        }),
        (None, {
            'classes': ('suit-tab', 'suit-tab-options',),
            'fields': ['crashed', 'painted']
        }),)


@pytest.mark.skip
@pytest.mark.django_gen_before('install', 'migrate')
@pytest.mark.django_gen('sample', """

#wehicle
---------
length: int
height: int

#car
-------
nr
mark
model
weight: int
crashed: bool(true)
painted: bool

@admin {
    fields: *, ^weight
    tabs: general(*), main(.*), options(crashed, painted)
}

""")
def test_admin_more_options_no_weight_and_parent():
    from sample.admin import CarAdmin
    from django.contrib.admin import ModelAdmin

    assert CarAdmin.suit_form_tabs == (
        ('general', 'General'),
        ('main', 'Main'),
        ('options', 'Options'),
    )

    assert CarAdmin.fieldsets == (
        (None, {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': ['length', 'height']
        }),
        (None, {
            'classes': ('suit-tab', 'suit-tab-main',),
            'fields': ['nr', 'mark', 'model']
        }),
        (None, {
            'classes': ('suit-tab', 'suit-tab-options',),
            'fields': ['crashed', 'painted']
        }),)


@pytest.mark.django_gen_before('install', 'migrate')
@pytest.mark.django_gen('admin_inline')
def test_admin_inlines():
    from admin_inline.admin import CarAdmin, CarServiceHistoryInline
    from admin_inline.models import Car, Service
    from django.contrib.admin import ModelAdmin

    from django.contrib.admin import TabularInline
    assert issubclass(CarServiceHistoryInline, TabularInline)

    assert CarAdmin.suit_form_tabs == (
        ('main', 'Main'),
        ('service', 'Service'),
    )

    assert CarServiceHistoryInline.model == Service
    assert CarServiceHistoryInline.fields == ['car', 'date', 'details']
    assert CarAdmin.inlines == [CarServiceHistoryInline]
