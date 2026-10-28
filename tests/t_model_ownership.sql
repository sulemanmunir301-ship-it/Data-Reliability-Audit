-- Fails for every model with no meta.owner. Ownership is the top-cited cause in the surveys
-- (see README), and it is the cheapest check to automate.
{% set missing = [] %}
{% for node in graph.nodes.values() %}
  {% if node.resource_type == 'model' and not node.config.meta.get('owner') %}
    {% do missing.append("'" ~ node.name ~ "'") %}
  {% endif %}
{% endfor %}
select unnest(cast([{{ missing | join(', ') }}] as varchar[])) as model_without_owner
