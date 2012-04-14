create temp table num_contractors as 
select count(*) from agg.b_contractor; 

create temp table num_jobs as 
select count(*) from agg.c_opening; 

