{
"id": "{{ record.id }}",
"title": "{{ record.title }}",
"desc" : "{{ record.desc }}",
"url": "{{ record.url }}",
"tags": [
	{% for tag in tags %}"{{ tag.concept.vocabulary.node_id }} {{ tag.concept.node_id }}"{% if not forloop.last %},{% endif %}
	{% endfor %}]
}