with source as (
    select * from {{ source('wc_raw', 'tournaments') }}
)

select
    tournament_id,
    year,
    -- Canonicalized via macros/canonicalize_team_name.sql.
    -- Original host_country and winner preserved for traceability.
    host_country as host_country_original,
    {{ canonicalize_team_name('host_country') }} as host_country,
    winner as winner_original,
    {{ canonicalize_team_name('winner') }} as winner,
    count_teams
from source
where tournament_name not ilike '%women%'
