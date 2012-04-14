select 
status, count(*) as num_contractors 
from agg.b_contractor 
group by status
