select 
status, count(*) as number_jobs 
from agg.b_opening 
group by status
