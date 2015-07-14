{
"title": "{{ record.title }}",
"desc" : "{{ record.description }}",
"notes": "{{ record.notes }}",
"name" : "{{ record.name }}",
"entry": "{{ record.node_id }}",
{% for tag in tags %}
"tag": "{{ tag.vocabulary.node_id }}/{{ tag.node_id }}",
{% endfor %}
}