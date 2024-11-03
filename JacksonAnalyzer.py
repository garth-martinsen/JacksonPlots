#file: JacksonAnalyzer.py: 10/24/2024 Reads/stores all.csv, Stores calculated fields. Plots fields vs dates.
#TODO: get file to accept matplotlib.pyplot as plt.

from tuples import Input_Entry, Output_Entry, Tot_Entry, plot_types
import csv
from datetime import datetime
import datetime
#import matplotlib.pyplot as plt

#Design: https://docs.google.com/document/d/1cpT-ntAGC8gtPLCb_U9wFLOqHPFSOs7ffgsplecqgcg/edit?tab=t.0
#Solutions: 
#1. Date: Read csv & store Dates as strings. For each plot, extract 2 lists: str<date>s, list<values>. 
# Convert list<str(date)> to list<datetime.date>

#TODO: 10/28/2024: Add the actual plotting ...
class JacksonAnalyzer:
    '''Reads all.csv, Stores Normalizers, extracts Lists for Plots.'''
    def __init__(self, data ):
        today = datetime.date.today()
        self._run_date = str(today)
        self.first_date = None    #computed in self.read_data(), after all data is read in.
        self.first_tot = None   # updated after summing all accounts in first date.
        self.input_file = f'/Users/garth/JacksonStocks/{data}'
        self.inputs_by_date = dict() #key: date  value: List<Entry>	
        self.firsts_by_id = dict() #key: id  value: value_USD
        self.tots_by_date = dict()  #key: date value:List<Entry>
        self.augments_by_date_id = dict() #key: (date, id)  value: (date,id,first_val,value, growth, alloc)
        self.output_by_id = dict() #key: id value: List<Output_Entry> built by using inputs_by_date, firsts*, tots_by_date
        self.ids = [109,115,123,145,222,365,690,713,999]  #last id is for Jackson totals
        self.plot_types= plot_types
        #print("attributes:", self.__dict__.keys())
        self.dates=[]     # populated after loading tots_by_date


    def get_plotting_dates(self,date_lst):
        '''Given a list of string dates, Returns a list of datetime dates'''
        plot_dates=[]
        for dt in date_lst:
            plot_dates.append(datetime.datetime.strptime(dt,"%m/%d/%Y").date())
        return plot_dates

       
    def read_data(self):
        '''Returns None. Reads in all.csv and stores them in input_by_date dict if they have balance > 0.00 key:date value:Entry'''
        with open(self.input_file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='\t')
            line_count = 0 
            for row in csv_reader:
                if line_count == 0:
                    print(f'Column names are {", ".join(row)}')
                    line_count += 1
                else:
                    #print(row)
                    date=row[0]
                    theId= int(row[2])
                    val = float(row[7])
                    tot = None
                    fract = None
                    growth = None
                    # if theId is in dict,return its list else return empty list, append entry to list and update dict.
                    # returns a list, either existing or empty
                    if val > 0.0:
                        flist = self.inputs_by_date.get(date, []) 
                        flist.append( Input_Entry(date, theId, row[1], row[3], row[4], row[5], row[6], val))
                        self.inputs_by_date[date]=flist     # update dict with updated list.
                        line_count += 1
        print(f'Stored {line_count} lines in dict, inputs_by_date: key:date, value: list<>.')
        self.first_date= list(self.inputs_by_date.keys())[0]
        sub_lst = []
        self.first_by_id = self.inputs_by_date[self.first_date]
        

    def populate_firsts(self):
        '''find or compute: first_date, firsts_by_id, first_tot, tots_by_date'''
        #first_date
        self.first_date = list(self.inputs_by_date.keys())[0]
        #firsts_by_id
         #TODO: load dict key: id, value: Input_Entry for id.
        for ntry in  self.inputs_by_date[self.first_date]:
            self.firsts_by_id[ntry.id]=ntry.value_USD
        #first_tot
        lst=[]
        for v in self.inputs_by_date[self.first_date]:
            lst.append(v.value_USD)
        self.first_tot = sum(lst)
        #first_jackson output tuple.first_value and value will be same(first_tot). growth, total, and alloc have no meaning.
        #namedtuple("Output_Entry", "     date,       id,   name,          first_value,     value, growth, total, alloc")
        first_jackson = Output_Entry(self.first_date, 999, 'jackson_total', self.first_tot, self.first_tot, None, None, None)
        listj = []
        listj.append(first_jackson)
        self.output_by_id[999]=listj 
        # tots_by_date will be used to compute alloc and tot_growth when populating outputs for plotting.
        for k,v in self.inputs_by_date.items():
            subs=[]
            for s in v:                         #sub account entries are found in lists of Input_Entry
                subs.append(s.value_USD)        #the value of stock, s, is found using the Input_Entry namedtuple
            self.tots_by_date[k]=(sum(subs),None)      #totalling all of the fund values gives the total for jackson, stored for that date.


    def populate_outputs(self):
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

    def show_fund(self, anId ):
        name= self.output_by_id[anId][0].name
        print ("Fund: ", anId, name)
        print( "---------------------------")
        for n in self.output_by_id[anId]:
            print(n.date, n.first_value, n.value, n.growth, n.total, n.alloc)

        #TODO: implement extraction of 2 lists for each plot, convert each list,date> to list<datetime.date>, pass to matplotlib.

    def show_all_funds(self):
        ids = list(self.output_by_id.keys())
        for i in ids:
            print()
            self.show_fund(i)


    def plot(self, name):
        '''calls functions with two lists for plotting(xarray, yarray). xarray will usually be dates which have been converted 
        from list<str> to list<datetime.date>  name:plot_type is one of: [vd, td, tgd, ad ]. see: tuples.Plot_Type'''
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


    def get_lists(self, search_list, x_ndx, y_ndx):
        '''search list is like; self.out_by_id[theId], x_ndx is index of date in tuple, y_ndx is index of value in tuple.'''
        x=[]
        y=[]
        for l in search_list:
            x.append(l[x_ndx])
            y.append(l[y_ndx])    
        return x,y


    def plot_fund_values(self, rows,cols):
        print(f"called  plot_values() with {rows} rows and {cols} columns") 
        fig, axs = plt.subplots(rows,cols,layout='constrained')
        k =0
        for theId in self.ids:
            ax = axs[k//3, k%3]
            x,y = self.get_lists(self.output_by_id[theId], 0, 4)
            name=self.output_by_id[theId][0].name
            ax.plot(x,y)
            ax.set(xlabel='date', ylabel='value($)', title=f'{name}:{theId}')
            k+=1
      
        


    def plot_fund_growths(self, rows, cols):
        ''' Nine Plots: grow by date for 9 ids, 999 being the last id.'''
        print(f"Called plot_growths() with {rows} rows and {cols} columns")
        fig, axs = plt.subplots(rows,cols,layout='constrained')
        k =0
        for theId in self.ids:
                ax = axs[k//3, k%3]
                x,y = self.get_lists(theId, 0, 5)
                name=self.output_by_id[theId][0].name
                ax.plot(x,y)
                ax.set(xlabel='date', ylabel='fund_growth(%)', title=f'{name}:{theId}')
                k+=1



    def plot_totals_with_growth(self, rows, cols):
        '''Two plots: 1)totals by date, and 2)total_growths by date '''
        print(f"Called plot_totals() with {rows} rows and {cols} columns. 1)totals by date, 2) total_growth by date.")
        fig, axs = plt.subplots(rows,cols,layout='constrained')
        k =0
        for theId in self.ids:
                ax = axs[k//2, k%2]
                x,y = self.get_lists(self.tots_by_date[thedate], 0, 5)
                name=self.output_by_id[theId][0].name
                ax.plot(dates,growths)
                ax.set(xlabel='date', ylabel='fund_growth(%)', title=f'{name}:{id}')
                k+=1
   

    def plot_fund_allocations(self, rows,cols):
        '''One Plot: with a line for each of the 8 funds ids. The allocations for each fund will change over dates'''
        print(f"Called plot_allocations() with {rows} rows and {cols} columns. Multi-line: one line for each id. alloc by date.")

