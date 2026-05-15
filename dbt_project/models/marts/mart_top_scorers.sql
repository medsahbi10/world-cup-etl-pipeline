-- Top scorers in men's World Cup history.
-- The INNER JOIN to stg_matches filters out women's WC goals (since stg_matches contains
-- only men's matches, women's match_ids find no match and get dropped).
-- own_goal = 0 excludes goals scored into a player's own net.

with goals as (
    select * from {{ source('wc_raw', 'goals') }}
),
mens_matches as (
    select * from {{ ref('stg_matches') }}
)

select
    g.player_id,
    g.given_name,
    g.family_name,
    g.player_team_name as country,
    count(*) as goals_scored
from goals g
inner join mens_matches m
    on g.match_id = m.match_id
where g.own_goal = 0
group by g.player_id, g.given_name, g.family_name, g.player_team_name
order by goals_scored desc
limit 20
