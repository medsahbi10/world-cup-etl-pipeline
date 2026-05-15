with matches as (
    select * from {{ ref('stg_matches') }}
),

home_perspective as (
    select
        home_team_canonical as team_name,
        home_team_score as goals_for,
        away_team_score as goals_against,
        case when result = 'home team win' then 1 else 0 end as is_win,
        case when result = 'draw'          then 1 else 0 end as is_draw,
        case when result = 'away team win' then 1 else 0 end as is_loss
    from matches
),

away_perspective as (
    select
        away_team_canonical as team_name,
        away_team_score as goals_for,
        home_team_score as goals_against,
        case when result = 'away team win' then 1 else 0 end as is_win,
        case when result = 'draw'          then 1 else 0 end as is_draw,
        case when result = 'home team win' then 1 else 0 end as is_loss
    from matches
),

all_team_matches as (
    select * from home_perspective
    union all
    select * from away_perspective
)

select
    team_name,
    count(*)                            as matches_played,
    sum(is_win)                         as wins,
    sum(is_draw)                        as draws,
    sum(is_loss)                        as losses,
    sum(goals_for)                      as goals_for,
    sum(goals_against)                  as goals_against,
    sum(goals_for) - sum(goals_against) as goal_difference
from all_team_matches
group by team_name
order by goals_for desc
