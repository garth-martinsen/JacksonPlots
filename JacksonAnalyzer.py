#file: JacksonAnalyzer.py: 10/24/2024 Reads/stores all.csv, Stores calculated fields. Plots fields vs dates.

from tuples import Input_Entry, Output_Entry, Tot_Entry, plot_types
import csv
from datetime import datetime

#Design: https://docs.google.com/document/d/1cpT-ntAGC8gtPLCb_U9wFLOqHPFSOs7ffgsplecqgcg/edit?tab=t.0
#Solutions: 
#1. Date: Read csv & store Dates as strings. For each plot, extract 2 lists: str<date>s, list<values>. 
# Convert list<str(date)> to list<datetime.date>

#TODO: 10/28/2024: Add the actual plotting ...
class JacksonAnalyzer:
    '''Reads all.csv, Stores Normalizers, extracts Lists for Plots.'''
    def __init__(self, data,first_date ):
        today = datetime.date.today()
        self._run_date = str(today)
        self.first_date = first_date
        self.first_tot = None   # updated after summing all accounts in first set.
        self.input_file = f'/Users/garth/JacksonStocks/{data}'
        self.inputs_by_date = dict() #key: date  value: List<Entry>	
        self.firsts_by_id = dict() #key: id  value: value_USD
        self.tots_by_date = dict()  #key: date value:List<Entry>
        self.augments_by_date_id = dict() #key: (date, id)  value: (date,id,first_val,value, growth, alloc)
        self.output_by_id = dict() #key: id value: List<Plot_Entry> built by using inputs_by_date, augments_by_date_id, tots_by_date
        self.ids = [109,115,123,145,222,365,690,713,999]  #last id is for Jackson totals
        #print("attributes:", self.__dict__.keys())


    def get_plotting_dates(lst):
        '''Given a list of string dates, Returns a list of datetime dates'''
        plot_dates=[]
        for dt in lst:
            plot_dates.append(datetime.datetime.strptime(theDate,"%m/%d/%Y").date())
        return plot_dates

       
    def read_data(self):
        '''Returns None. Reads in all.csv and stores it in input_by_date dict key:date value:Entry'''
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
                    flist = self.inputs_by_date.get(date, []) 
                    flist.append( Input_Entry(date, theId, row[1], row[3], row[4], row[5], row[6], val))
                    self.inputs_by_date[date]=flist     # update dict with updated list.
                    line_count += 1
        print(f'Stored {line_count} lines in dict, inputs_by_date: key:date, value: list<>.')


    
    def populate_augments(self):

        '''Finds 1stValue for each id, first_val. Computes Totals for each date, current_total. Computes id_growth for each date.
           Computes tot_growth for each date, tot_growth. Computes allocation for each (date,id).'''

		# find Value for each id on first date:
        first_vals = self.inputs_by_date[self.first_date]
        for item in first_vals:
            self.firsts_by_id[item.id]=item.value_USD        

        # find total Value for first date:
        self.first_tot= sum([x.value_USD for x in self.inputs_by_date[self.first_date]])
        #TODO: fix: 109 ('10/9/2024', 109, 'JNL/JPMorgan U.S. Government & Quality Bond', 19447.0, 19447.0, 0.0, ('10/9/2024', 76518.3, 76518.3, 0.0), 25.41). remove the "(s" so that a fetch from self.output_by_id[109] shows just the fields without the embeds.  
        #TODO: Build Output_Entry from Input_Entry plus computedfields. 
        # Populate dict, self.output_by_id (key=id value:Output_Entry)         
        # find val_growth & alloc for each id. Find first_tot, tot, & tot_ growths for each date.
        # Use formula: growth(%)= (first/current -1) * 100 ;  formula: alloc = id.value/tot * 100.0 
        for dt, lst in self.inputs_by_date.items():
           growth=0.0
           first_tot = self.first_tot
           current_tot = sum([x.value_USD for x in lst])
           tot_growth = round(((current_tot/first_tot)-1) * 100.0,2)
           tot_tuple = (dt, first_tot, current_tot, tot_growth)
           self.tots_by_date[dt]=tot_tuple
           tot_output_entry = (dt, 999, 'Jackson', first_tot, current_tot, tot_growth, None, None)
           self.augments_by_date_id[(dt,999)]=tot_output_entry 
           for i in lst:
               theId=i.id
               if theId != 0:
                  firstVal=self.firsts_by_id[theId]
                  if firstVal != 0 and i.value_USD != 0:
                     current_value= i.value_USD
                     growth = round(((current_value/firstVal)-1) * 100.0,2)
                     alloc  = round((current_value/current_tot)*100.0,2)
                     self.augments_by_date_id[(dt,theId)]= (dt,theId,i.name, firstVal, current_value, growth, current_tot, alloc)

    def populate_output(self):
        ''' Populate self.output_by_id dict using dicts: self.input_by_date, self.augmennts_by_date_id, and self.tots_by_date'''
        #namedtuple("Input_Entry", "date, id, name, future, units, unitVal_USD, alloc_csv, value_USD")
        #namedtuple("Output_Entry", "date, id, name, first_value, value, growth, total, alloc")
        #augments_by_date_id = dict() #key: (date, id)  value: (date,id,name, first_val,value, growth, alloc)
        for k, v in self.augments_by_date_id.items():
                date, theId, name, first_val, val, growth, tot, alloc = v 
                tot = self.tots_by_date[date]
                if theId != 999:
                    theList = self.output_by_id.get(theId,[])   #return empty list if new.
                    theList.append( (date,theId,name, first_val, val,growth,tot, alloc))
                    self.output_by_id[theId]=theList
                else:
                   self.output_by_id[theId] = self.augments_by_date_id[(date,theId)]

       # self.output_by_id should now be populated with all of the input data plus the augmented data.




    def extract_plot_data(self, name):
        '''returns two lists for plotting(xarray, yarray). xarray will usually be dates which have been converted 
        from list<str> to list<datetime.date>  name:plot_type is one of: [vd, td, vgd, tgd, ad ]
        type      description:
        vd        fund value by date
        td        total of funds by date
        vgd       growth of value by date
        tgd       growth of total by date
        ad        allocated percentage by date '''
        #TODO: implement extraction of 2 lists for each plot, convert each list,date> to list<datetime.date>, pass to matplotlib.
        match name:

            case 'vd':    #fund value by date
                 action-1
            case 'td':    #total of funds by date
                 action-2
            case 'vgd':   #growth of fund value by date
                 action-3
            case 'tgd':   #growth of total by date
                 action-4
            case 'ad':    #allocation of fund by date.
                 action-5
            case _:
                    action-default 
'''
        # find Totals for each date. 
        for dt, lst in self.by_date.items():
           Total_dt= sum[x.value_USD for x in lst]
           self.totals_by_date[dt] = Total_dt

        # find fracts for each date. 
        for dt, lst in self.by_date.items():
            for l in lst:
                    self.fracts_by_date[dt]=(l.id, l.value_USD/self.st    

    def populate_normalized (self):
        Returns nothing, but self.by_date is updated so all fields are populated
        sums all id.value_USB to get tot4date and first_tot. sets normalized(date, id, name, value_USD, 
        first_val, tot4date, first_tot). 
        Then for all dates using first_val and first_tot populate all normalized fields.

        #namedtuple("Normalized", "date, id, name, value_USD, first_val, tot4date, first_tot, id_growth, id_alloc")       
        vals=[]
        tots =[]   
        for id in self.ids:
            for ntry in self.by_date[id]
                if ntry.date == self.first_date:
#TODO; finish from here: populate the self.normalized with data from self.by_date.
        first_lst = self.byfund[self.first_date]
        for ntry in first_lst:
            vals.append(ntry.value_USD)
            self.normalized.append(Normalized(ntry.date, ntry.id, ntry.value_USD, ntry.value_USD, None, None, None, None))
        self.first_tots = sum(vals)

        # with first_val and first_tot we can finish up the normalization of each record in self.by_date
        for id, ntry in self.normalized.items():
            self.normalized[date]= Normalized(ntry.date,id, ntry.name, ntry.value_USD,ntry.first_val, ntry.tot4date,
                                              self.first_tots, (ntry.value_USD/ntry.first_val -1)*100, 
                                              ntry.value_USD/ntry.tot4date)  
        
     
    def extract_id_growths(self, id):
        Uses nomalized dict to create List<growths> for id. 
        Returns List<growths> for id for each date.
        dates=[]
        growths=[]
        for id, norm in self.normalize.items():
           dates.append(norm.date)
           growths.append(norm.growth)
        return dates, growths


    def extract_tot_growths(self):
         Returns List<dates>, List<tot_growths> Uses first_tot to compute tot_growth for each record. 
        Returns List<date>, List<tot_growth>

        # tuples (date, tot4date/first_tot). Iterating self.normalized will input duplicate pairs and dates 
        # but set will reject the dups in each.        
        tot_growths=set()
        t_growths=[] 
        dates=set()
        for date, ntry in self.normalized.items():
            tot_growths.add((date,ntry.tot4date/self.first_tots[date]))  #adding pairs into set.

        #creating list from set by popping and appending pair to list...    
        for i in range(len(tot_growths)):
            m=tot_growths.pop()
            t_growths.append(m)
        # using list comprehension to extract elements of each pair into two lists.  
        tots = [x[1] for x in t_growths ]
        dts= [x[0] for x in t_growths]        
        return dts,tots 
            

    def extract_allocs(self):
         Uses value_USD and tot4date to compute alloc for each date. Returns List<allocs>
        tot_portions = set()
        alloc_lst = []

        for date, ntry in self.normalize.items():
            tot_portions.add((date, ntry.alloc))

        for i in range(len(tot_portions)):
            m=tot_portions.pop()
            alloc_lst.append(m)
   
        dts=[x[0] for x in alloc_lst]
        allocs= [x[1] for x in alloc_lst]
        return dts,allocs

 
    def plot(self,alist):     
        noop
'''
