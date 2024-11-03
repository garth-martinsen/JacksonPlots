#file: tuples.py 10/24/2024 Contains namedtuples: Entry and Augmented. All plots will come from augemented tuple

from collections import namedtuple

'''Entry namedtuple will hold all fields read from all.csv entries. 
Normalized namedtuple  will hold date,id,name, current_value(value_USD),then 
computed values: first_value, tot4date, growth, alloc. first_val is the id.value_USD and will be 
used to compute growth,all fund.value_USDs will be used to compute current_tot, which will be used 
to compute alloc . Note: Regular tuples can be added to get a consolidated tuple. t1=(1,2,3,4) t2=(5,6,7,8)
t1+t2= (1, 2, 3, 4, 5, 6, 7, 8)'''
#last two values in Entry will be added after dict self.tots_by_date is populated.
Input_Entry = namedtuple("Input_Entry", "date, id, name, future, units, unitVal_USD, alloc_csv, value_USD") 
Output_Entry = namedtuple("Output_Entry", "date, id, name, first_value, value, growth, total, alloc")
# populated for dict  self.tots_by_date after first_val and first_tot are computed.
Tot_Entry =namedtuple("Tot_Entry", "date, first_tot, current_tot, tot_growth")  
Plot_Types =namedtuple("Plot_Types", "values_by_date, fund_growth_by_date, totals_by_date, allocations_by_date ")
plot_types = Plot_Types("vd","vgd", "td", "ad")
  
#from tuples import Input_Entry, Output_entry, Tot_Entry, plot_types

