-- Maps historical/political team names to their modern continuous-history equivalents,
-- so analytics treat "the German team" as one continuous entity across eras.
--
-- Currently handles: West Germany / East Germany  ->  Germany
-- Extend by adding more WHEN clauses (Soviet Union -> Russia, Czechoslovakia -> Czech Republic, etc.).
--
-- Usage:
--   {{ canonicalize_team_name('home_team_name') }} as home_team_canonical
{% macro canonicalize_team_name(team_column) %}
    case
        when {{ team_column }} in ('West Germany', 'East Germany') then 'Germany'
        else {{ team_column }}
    end
{% endmacro %}
