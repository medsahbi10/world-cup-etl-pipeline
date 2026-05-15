-- Every men's World Cup: year, host, winner, number of teams.
-- Sourced entirely from stg_tournaments — no joins or aggregation needed.
select
    year,
    host_country,
    winner,
    count_teams
from {{ ref('stg_tournaments') }}
order by year
