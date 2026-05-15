-- For each men's World Cup, summarize the host country's performance at home.
-- Answers: do host countries perform exceptionally well at their home WC?

with t as (select * from {{ ref('stg_tournaments') }}),
     m as (select * from {{ ref('stg_matches') }}),

-- One row per match-the-host-played, normalized to "host's perspective"
host_matches as (
    select
        t.year,
        t.host_country,
        t.winner,
        case
            when m.home_team_canonical = t.host_country then m.home_team_score
            when m.away_team_canonical = t.host_country then m.away_team_score
        end as host_goals,
        case
            when m.home_team_canonical = t.host_country then m.away_team_score
            when m.away_team_canonical = t.host_country then m.home_team_score
        end as opp_goals
    from m
    inner join t on m.tournament_id = t.tournament_id
    where t.host_country in (m.home_team_canonical, m.away_team_canonical)
)

select
    year,
    host_country,
    case when host_country = winner then 'YES' else 'no' end as host_won_their_wc,
    count(*)         as host_matches,
    sum(host_goals)  as goals_scored,
    sum(opp_goals)   as goals_conceded
from host_matches
group by year, host_country, winner
order by year
