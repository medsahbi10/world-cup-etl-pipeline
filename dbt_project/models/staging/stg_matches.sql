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
    -- Map historical team names to their modern equivalents.
    -- Original home_team_name is preserved above for traceability.
    case
        when m.home_team_name in ('West Germany', 'East Germany') then 'Germany'
        else m.home_team_name
    end as home_team_canonical,
    m.away_team_id,
    m.away_team_name,
    m.away_team_code,
    case
        when m.away_team_name in ('West Germany', 'East Germany') then 'Germany'
        else m.away_team_name
    end as away_team_canonical,
    m.home_team_score,
    m.away_team_score,
    m.result,
    m.extra_time,
    m.penalty_shootout
from source as m
inner join {{ ref('stg_tournaments') }} as t
    on m.tournament_id = t.tournament_id
