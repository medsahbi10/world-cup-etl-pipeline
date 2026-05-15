-- By default dbt prefixes custom schemas with the target schema name
-- (e.g. `+schema: wc_gold` becomes `wc_silver_wc_gold`).
-- This override makes dbt use the custom schema name AS-IS, which is what we want.
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
