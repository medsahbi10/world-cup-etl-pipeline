with source as (
    select * from {{ source('wc_raw', 'tournaments') }}
)

select
    tournament_id,
    year,
    host_country,
    winner,
    count_teams
from source
where tournament_name not ilike '%women%'
