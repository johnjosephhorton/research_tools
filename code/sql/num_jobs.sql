select 
status, count(*) as num_jobs 
from agg.b_opening 
group by status
