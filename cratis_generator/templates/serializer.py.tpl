
{% for extra in rest_conf.extra_serializers  %}
{% with rest_conf=extra %}
{% include 'serializer.py.tpl' %}
{% endwith %}
{% endfor %}

class {{ rest_conf.serializer_name }}Serializer(serializers.ModelSerializer):
    {% for name, declaration in rest_conf.field_declarations %}
    {{ name }} = {{ declaration }}{% endfor %}

    class Meta:
        model = {{ rest_conf.collection.class_name }}
        fields = ['{{ rest_conf.field_names|join("','") }}']
        {% if rest_conf.read_only_fields %}read_only_fields = ['{{ rest_conf.read_only_fields|join("','") }}']{% endif %}

    {% if rest_conf.is_writable and rest_conf.is_root %}
    def create(self, validated_data):
        {% for extra in rest_conf.extra_serializers  %}{% if extra.is_writable %}
        {{ extra.parent_field.name }}_data = validated_data.pop('{{ extra.parent_field.name }}')
        {% endif %}{% endfor %}

        item = {{ rest_conf.collection.class_name }}.objects.create(
            {% if rest_conf.user_field %}{{ rest_conf.user_field }}=self.context.get('request').user, {% endif %}**validated_data)

        {% for extra in rest_conf.extra_serializers  %}{% if extra.is_writable %}
        for data in {{ extra.parent_field.name }}_data:
            {{ extra.collection.class_name }}.objects.create({{ extra.parent_field.source_field_name }}=item,{% if extra.user_field %}{{  extra.user_field }}=self.context.get('request').user, {% endif %}**data)
        {% endif %}{% endfor %}

        {{ rest_conf.on_create|indent(8) }}

        return item
    {% endif %}

    {% if col.polymorphic %}
    def to_representation(self, obj):
        """
        Polymorphic serialization
        """
        {% for child in col.child_collections %}
        {% if child.rest %}
        if isinstance(obj, {{ child.class_name }}):
            return {{ child.class_name }}Serializer(obj, context=self.context).to_representation(obj)
        {% endif %}
        {% endfor %}

        return super().to_representation(obj)
    {% endif %}

