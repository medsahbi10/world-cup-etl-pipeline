with source as (
    select * from {{ source('wc_raw', 'matches') }}
)

select
    m.tournament_id,
    m.match_id,
    m.match_date,
    m.stage_name,
    m.home_team_id,
    m.home_team_name,
    m.home_team_code,
    -- Canonicalized via macros/canonicalize_team_name.sql. Original
    -- home_team_name is preserved above for traceability.
    {{ canonicalize_team_name('m.home_team_name') }} as home_team_canonical,
    m.away_team_id,
    m.away_team_name,
    m.away_team_code,
    {{ canonicalize_team_name('m.away_team_name') }} as away_team_canonical,
    m.home_team_score,
    m.away_team_score,
    m.result,
    m.extra_time,
    m.penalty_shootout
from source as m
inner join {{ ref('stg_tournaments') }} as t
    on m.tournament_id = t.tournament_id
