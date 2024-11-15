#file: JacksonAnalyzer.py: 10/24/2024 Reads/stores all.csv, Stores calculated fields. Plots fields vs dates.

from tuples import Input_Entry, Output_Entry, Tot_Entry, plot_types
import csv
from datetime import datetime
import datetime
import matplotlib.pyplot as plt
import numpy as np


#Design: https://docs.google.com/document/d/1cpT-ntAGC8gtPLCb_U9wFLOqHPFSOs7ffgsplecqgcg/edit?tab=t.0
#Solutions: 
#1. Date: Read csv & store Dates as strings. For each plot, extract 2 lists: str<date>s, list<values>. 
# Convert list<str(date)> to list<datetime.date>

#TODO: 10/28/2024: Add the actual plotting ...
#TODO: 11/12/2024: Refactor to reduce lines of code....


#numpy fields of processed  data used for analysis and plotting
dt_j=dt_j=np.dtype([
             ('date', np.dtype(str),10),
             ('id', np.dtype(int)),
             ('name', np.dtype(str),55),
             ('value', np.dtype(float)),
             ('growth', np.dtype(float)),
             ('alloc', np.dtype(float)) ])


#TODO: 11/12/2024: Remove constructor arg data, and just hard code it to be all.csv Done: lines: 33, 38
class JacksonAnalyzer:
    '''Reads all.csv, Stores Normalizers, extracts Lists for Plots.'''
    def __init__(self):
        today = datetime.date.today()
        self._run_date = str(today)
        self.first_date = None    #computed in self.read_data(), after all data is read in.
        self.first_tot = None   # updated after summing all accounts in first date.
        self.input_file = f'/Users/garth/JacksonStocks/all.csv'
        self.inputs_by_date = dict() #key: date  value: List<Entry>	
        self.firsts_by_id = dict() #key: id  value: value_USD
        self.tots_by_date = dict()  #key: date value:List<Entry>
        self.output_by_id = dict() #key: id value: List<Output_Entry> built by using inputs_by_date, firsts*, tots_by_date
        self.attrib_by_id_date={}  #key:(id,date) value: list<Entry>
        self.ids = [109,115,123,145,222,365,690,713,999]  #last id is for Jackson totals
        self.plot_types= plot_types
        self.nparrays_by_id={}
        #print("attributes:", self.__dict__.keys())
        self.dates=[]     # populated after loading tots_by_date


    def get_plotting_dates(self,date_lst):
        '''Given a list of string dates, Returns a list of datetime dates'''
        print("datestr: ", date_lst)
        plot_dates=[]
        for dt in date_lst:
            plot_dates.append(datetime.datetime.strptime(dt,"%m/%d/%Y").date())
        return plot_dates
 

    def iso_date(self, str_date):
        return datetime.datetime.strptime(str_date,"%m/%d/%Y").date()

    def day_of_year(self, str_date):
        '''Uses last digit in str_date = yr Converts str_date to iso_date,get day-of-yr (doy) fract=  (doy/365) => 
        round (yr+fract) to 2 decimal places. eg 11/11/2024 => 4.87 and 1/5/2025 => 5.01. This unclutters x_axis in plots by date'''  
        yr=str_date[-1:]
        idate=self.iso_date(str_date)
        doy = idate.timetuple().tm_yday
        return yr,round(int(yr)+doy/365,2)
        

    def process(self):
        self.firsts()
        self.outputs()
        self.store_nparrays_by_id()
       
    def read_data(self):
        '''Returns None. Reads in all.csv and stores them in input_by_date dict if they have balance > 0.00 key:date value:Entry'''
        with open(self.input_file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='\t')
            line_count = 0 
            for row in csv_reader:
                if line_count == 0:
                    #print(f'Column names are {", ".join(row)}')
                    line_count += 1
                else:
                    #print("row length:",len(row),row)
                    date=row[0]
                    theId= int(row[2])
                    val = float(row[7])
                    tot = None
                    fract = None
                    growth = None
                    #TODO: Change so that dict values are dt_j tuples. This will reduce the number dicts needed
                    # if theId is in dict,return its list else return empty list, append entry to list and update dict.
                    # returns a list, either existing or empty
                    if val > 0.0:
                        flist = self.inputs_by_date.get(date, []) 
                        # change: Do not use namedtuple, only need the dt_j values and the tuple representing them...
                        flist.append( Input_Entry(date, theId, row[1], row[3], row[4], row[5], row[6], val))
                        self.inputs_by_date[date]=flist     # update dict with updated list.
                        line_count += 1
        #print(f'Stored {line_count} lines in dict, inputs_by_date: key:date, value: list<>.')
        print(f" Read: {line_count} records")
        self.first_date= list(self.inputs_by_date.keys())[0]
        sub_lst = []
        self.first_by_id = self.inputs_by_date[self.first_date]
        

    def firsts(self):
        '''find or compute: first_date, firsts_by_id, first_tot, tots_by_date'''
        #first_date
        self.first_date = list(self.inputs_by_date.keys())[0]
        #firsts_by_id
        for ntry in  self.inputs_by_date[self.first_date]:
            self.firsts_by_id[ntry.id]=ntry.value_USD
        #first_tot
        lst=[]
        for v in self.inputs_by_date[self.first_date]:
            lst.append(v.value_USD)
        self.first_tot = sum(lst)
        #first_jackson output tuple.first_value and value will be same(first_tot). growth, total, and alloc have no meaning.
        # tots_by_date will be used to compute alloc and tot_growth when populating outputs for plotting.
        for k,v in self.inputs_by_date.items():
            subs=[]
            for s in v:                         #sub account entries are found in lists of Input_Entry
                subs.append(s.value_USD)        #the value of stock, s, is found using the Input_Entry namedtuple
            self.tots_by_date[k]=(sum(subs),None) #totalling all of the fund values gives the total for jackson, stored for that date.


    def outputs(self):
        '''Create self.output_by_id, using inputs_by_date, firsts, tots_by_date'''
        # populate the output_by_id dict, iterating over ids and dates. 
        #namedtuple("Output_Entry", "date, id, name, first_value, value, growth, total, alloc")
        for k,v in self.inputs_by_date.items():
           date = k
           for s in v:
               anId= s.id
               name= s.name
               #print("anId", anId)
               first_val = self.firsts_by_id[anId]
               value = s.value_USD
               growth = round(((value/first_val -1) * 100), 2)    # percent rounded to 2 decimal places
               tot = self.tots_by_date[date][0]
               alloc = round((value/tot * 100.0),2)
               lst = self.output_by_id.get(anId, [])   # returns a list, populated or empty.
               lst.append( Output_Entry(date, anId, name, first_val, value, growth, tot, alloc ) )
               self.output_by_id[anId]=lst
           #add jackson total as id: 999 
           tot = self.tots_by_date[date][0]
           first_tot = self.first_tot
           tot_growth = round((( tot/first_tot - 1) * 100.0), 2)
           self.tots_by_date[date]=(tot,tot_growth)
           lst = self.output_by_id.get(999,[])
           lst.append(Output_Entry(date, 999, 'jackson', self.first_tot, tot, tot_growth, None, None))
           self.output_by_id[999]=lst
        # store all date strings in self.dates.
        for dt in self.tots_by_date.keys():
            self.dates.append(dt)           # now contains all dates in str form.
#TODO: Fix: id is always 999, needs to show real fund_id not 999. Done! There are 9 groups and each shows it id on every line.
    def show_fund(self, anId ):
        name= self.output_by_id[anId][0].name
        print ("Fund: ", anId, name)
        print( "---------------------------------------------")
        print('id, date,     first,  value,  growth, jtotal, alloc')
        for n in self.output_by_id[anId]:
            print(n.id, n.date, n.first_value, n.value, n.growth, n.total, n.alloc)

    def show_all_funds(self):
        ids = list(self.output_by_id.keys())
        for i in ids:
            print()
            self.show_fund(i)




    #TODO:Dates are too crowded for x-axis. Try using int(yyyy[-1]) and add day-of-year/365 and round to 2 decimal places eg: 4.83
    #TODO: Show range of dates in title. Done 
    def store_nparrays_by_id(self):
        '''Process: iterate thru ids and get list<id> using: lst_109=ja.output_by_id[109];iterate thru lst_109 creating list<tuple>,
        list_t_109, where tupleis (date,id,name,value, growth, alloc); then create array_109= np.array(list_t_109,dt_j); store the 
        nparray in self.nparrays_by_id for later use.  later, extract arrays for plotting by :nparray = 
        self.nparrays_by_id[anId]['x_name'] or['y_name']. On x axis, dates shown like: 4.83: 2024 doy/365''' 
        #self.nparrays_by_id={} created in constructor...
        #TODO: use day of year, doy for dates in plots...Done
        for i in self.ids:
           t_list=[]
           for e in self.output_by_id[i]:
               yr,doy= self.day_of_year(e.date)
               t_list.append((doy, e.id, e.name, e.value, e.growth, e.alloc))
           nparray = np.array(t_list, dt_j)
           self.nparrays_by_id[i]=nparray
           
    #TODO: Change so that subplots:331-339 are used; show date-range in title: Done.ln: 215-217, 223, 225
    def plot_by_id(self, subplots, x_name, y_name):
        '''There are 9 ids, with last being 999 (jackson). Arg subplots is 331(3x3) Each id subplot increments by 1.
        Title includes id, plot_type, date range'''
        fig=plt.figure()
        subplot=subplots       #first subplot in series.            
        start = self.dates[0]
        end= self.dates[-1]

        for anId in self.ids:
            nparray = self.nparrays_by_id[anId]
            x= nparray[x_name]
            y = nparray[y_name]
            plt.subplot(subplot)
            plt.plot(x, y)
            plt.title(f'{str(anId)} {y_name} from {start} to {end}')
            plt.grid(True)
            subplot +=1
        plt.show()
        fig.savefig(f"Fund_{y_name}.png")


    def plot_totals_with_growth(self, subplots):
        '''Two plots: 1)totals by date, and 2)total_growths by date '''
        print(f"Called plot_totals_with_growth({subplots}) The two subplots will be totals_by_date:{subplots}, total_growth_by_date: {subplots +2}.")
        start = self.dates[0]
        end= self.dates[-1]
        fig=plt.figure()
        nparray = self.nparrays_by_id[999]
        x = nparray['date']
        y = nparray['value']
        plt.subplot(subplots)
        plt.plot(x,y)
        plt.title(f'999: Jackson Totals from {start} to {end}')
        plt.grid(True)

        # plot tot_growth by date.
        y = nparray['growth']
        plt.subplot(subplots +2)
        plt.plot(x,y)
        plt.title(f'999: Jackson Totals_Growth from {start} to {end}')
        plt.grid(True)

        plt.show()
        fig.savefig("Totals.png")
    

    #TODO: Debug stack_plot_allocations
    def stack_plot_allocations(self):
        alloc_lst= []
        lable_lst=[]
        # build array rows = ids cols: alloc by date.
        for i in self.ids:
            if i != 999:
                lable_lst.append(str(i))
                alloc_lst.append(self.nparrays_by_id[i]['alloc'])
        alloc_array = np.array(alloc_lst)
        start = self.dates[0]
        end= self.dates[-1]
        theDates=[]
        for dt in self.dates:
            theDates.append( self.day_of_year(dt)[1])
        x = np.array((theDates))
        fig, ax = plt.subplots()
        plt.stackplot( x, alloc_array, labels=(lable_lst))
        ax.legend(loc='lower center', reverse=True)
        ax.set_title(f'Jackson fund allocations from {start} to {end}')
        ax.set_xlabel('date')
        ax.set_ylabel('% of Total')
        plt.show()
        fig.savefig("Allocations.png")
	
'''
------------------------------keep below---------------
    def plot(self, name):
        comment: calls functions with two lists for plotting(xarray, yarray). xarray will usually be dates which have been converted 
        from list<str> to list<datetime.date>  name:plot_type is one of: [vd, td, tgd, ad ]. see: tuples.Plot_Type
        match name:

            case 'vd':    #fund value by date
                self.plot_fund_values(3,3)
            case 'vgd':   #growth of funds by date
                self.plot_fund_growths(3,3)
            case 'td':    #total of funds by date, also total_growth by date
                self.plot_totals_with_growth(1,2)
            case 'ad':    #allocation of fund by date.
                self.plot_fund_allocations(1,1)
            case _:
                values= list(self.plot_types._asdict().values())
                print('Error: ',name, '  is not a valid plot_type. should be one of: ',values)



        markers_by_id = dict()
        markers_by_id[109]="<"
        markers_by_id[115]=">"
        markers_by_id[123]="8"
        markers_by_id[145]="s"
        markers_by_id[222]="1"
        markers_by_id[365]="2"
        markers_by_id[690]="3"
        markers_by_id[713]="4"
        print(markers_by_id )


StackPlot:
Axes.stackplot(x, *args, labels=(), colors=None, hatch=None, baseline='zero', data=None, **kwargs)[source]

ax.stackplot(year, population_by_continent.values(),
             labels=population_by_continent.keys(), alpha=0.8)
ax.legend(loc='upper left', reverse=True)
ax.set_title('World population')
ax.set_xlabel('Year')
ax.set_ylabel('Number of people (billions)')

Marker plot:
 for i in self.ids:$
                if i != 999:$ 
                 for dt in self.dates:$
                     x=attrib_by_id_date[(i,dt)][0]$
                     y=attrib_by_id_date[(i,dt)][1]$
                     ax.stackplot(x, y, markers_by_id[i])$
                     ax.grid()$

***To Get tuples of (id, alloc) by date, do:
for i,o in ja.output_by_id.items():
...     if i != 999:                                  #exclude any entries for jackson id:999
...         for l in o:
...             lst= id_alloc_by_date.get(l.date,[])  # get list to hold tuples, empty or in-progress list.
...             lst.append( ( l.id, l.alloc) )        # add the tuple for date (l.date).
...             id_alloc_by_date[l.date]=lst
'''
