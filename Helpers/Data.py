import pandas as pd
import numpy as np


cat_1 =  "Cat_1"
dtypes = {'OrderID': int, 'Cat_1': str, 'Item': str, 'Amount': float, 'Option_1': str, 'Amount_1': str, 'Option_2': str, 'Amount_2': str}

class Menu:
    def __init__(self, filename):
        self.filename = filename
        self.df = pd.read_excel(filename, sheet_name = None, index_col = 0, dtype = dtypes)
        self.food = {}
        self.price = {}
        self.cat = {}
        # List of restaurants
        self.restaurants = list(self.df.keys())

        spl_to_str = lambda s : np.asarray(s.split(",")).astype(str) if type(s) is str else s
        spl_to_float = lambda s : np.asarray(s.split(",")).astype(float) if type(s) is str else s
        # Process data
        for r in self.restaurants:
            r_data = self.df[r]

            # Format strings into arrays
            r_data.iloc[:,[3,5]] = r_data.iloc[:,[3,5]].applymap(spl_to_str)
            r_data.iloc[:,[4,6]] = r_data.iloc[:,[4,6]].applymap(spl_to_float)
            
            # Price data frame
            self.price[r] = pd.merge(pd.merge(r_data.iloc[:,2], r_data.iloc[:,4], on = 'OrderID'), r_data.iloc[:,6], on = 'OrderID')

            # Item data frame
            self.food[r] = pd.merge(pd.merge(r_data.iloc[:,1], r_data.iloc[:,3], on = 'OrderID'), r_data.iloc[:,5], on = 'OrderID')

            # Cat data frame
            self.cat[r] = pd.DataFrame(r_data.iloc[:,0])
            self.cat[r].insert(1, "Avail", True)

    def from_tuple_to_cost(self, restaurant, ID):
        ans = [None]*len(ID)
        id = ID[0]
        ans[0] = self.price[restaurant].iloc[:,0].loc[id] if id is not None else 0
        ans[1] = self.price[restaurant].iloc[:,1].loc[id][int(ID[1])] if ID[1] is not None else 0
        ans[2] = self.price[restaurant].iloc[:,2].loc[id][int(ID[2])] if ID[2] is not None else 0
        return sum(ans)

    def cost(self, restaurant, ID):
        #check if key exists
        if ID in (self.price[restaurant].index):
            output = self.price[restaurant].iloc[:,0].loc[ID]
            return output
        
        else:
            return print("Error: ID does not exist")

    def list_of_cost_options(self, restaurant, ID, option):
        output = self.price[restaurant].iloc[:,option].loc[ID]
            
        return output if not np.any(np.isnan(output)) else None

    def from_tuple_to_item(self, restaurant, ID):
        ans = [None]*len(ID)
        id = ID[0]
        ans[0] = self.food[restaurant].iloc[:,0].loc[id] if id is not None else ""
        ans[1] = self.food[restaurant].iloc[:,1].loc[id][int(ID[1])] if ID[1] is not None else ""
        ans[2] = self.food[restaurant].iloc[:,2].loc[id][int(ID[2])] if ID[2] is not None else ""
        return ' '.join(filter(None,ans))

    def item(self, restaurant, ID):
        #check if key exists
        if ID in (self.food[restaurant].index):
            output = self.food[restaurant].iloc[:,0].loc[ID]

            # output can be either array or string
            if type(output) is np.float64:
                return output if not np.isnan(output) else None
            else:
                return output
        else:
            return print("Error: ID does not exist")

    def list_of_item_options(self, restaurant, ID, option):
        output = self.food[restaurant].iloc[:,option].loc[ID]

        # output can be either array or string
        if type(output) is np.float64:
            return output if not np.isnan(output) else None
        else:
            return output

    def list_of_items(self, restaurant, list_of_ID = None):
        if list_of_ID is None:
            return self.food[restaurant].iloc[:,0].tolist()
        else:
            return self.food[restaurant].iloc[list_of_ID,0].tolist()

    def list_of_costs(self, restaurant, list_of_ID = None):
        if list_of_ID is None:
            return self.price[restaurant].iloc[:,0].tolist()
        else:
            return self.price[restaurant].iloc[list_of_ID,0].tolist()

    def list_of_ID(self, restaurant):
        return self.df[restaurant].index.to_numpy().tolist()
    
    def rests(self):
        return self.restaurants

    def list_of_cat(self, r):
        subset = self.cat[r].loc[self.cat[r].iloc[:,1] == True]
        return dict.fromkeys(subset.iloc[:,0].tolist())

    def show_cat(self, r):
        return dict.fromkeys(self.cat[r].iloc[:,0].tolist())
    
    def cat_subset(self, r, cat):
        subset = self.cat[r].loc[self.cat[r].iloc[:,0] == cat]
        subset = subset.loc[subset.iloc[:,1] == True]
        return subset.index.to_numpy().tolist()
    
    def cat_subset_all(self, r, cat):
        subset = self.cat[r].loc[self.cat[r].iloc[:,0] == cat]
        return subset.index.to_numpy().tolist()

    def block_order(self, r, id):
        self.cat[r].loc[id,"Avail"] = False
    
    def unblock_order(self, r, id):
        self.cat[r].loc[id,"Avail"] = True

    def check_avail(self, r, id):
        return self.cat[r].loc[id,"Avail"]

        
class StoreData:
    def __init__(self, list_of_stores = np.empty(0, dtype=str), list_of_ids = np.empty(0, dtype=str)):
        self.list_of_stores = list_of_stores
        self.list_of_ids = list_of_ids
        self.df = pd.DataFrame(
            {'ID': list_of_ids, 'Stores': list_of_stores})

    def ID(self, store):
        df1 = self.df.set_index("Stores")
        return int(df1.loc[store].loc['ID'])
    
    def stores(self, ID):
        df1 = self.df.set_index("ID")
        return df1.loc[ID].loc['Stores']

    def toList(self, data):
        return self.df.loc[:,data]

    def changeID(self, index, ID):
        self.list_of_ids[index] = ID
        self.df.iloc[index,0] = ID
        return self.df.iloc[index,1]

menu = Menu("Menu.xlsx")
r = "Ah Lian Food"
# list_of_residence = ["Eusoff Hall", "Kent Ridge Hall", "King Edward VII Hall", "Raffles Hall", "Sheares Hall", "Temasek Hall", "PGP House", "CAPT", "Tembusu", "RVRC", "RC4", "Cinnamon"]
# dict_of_residence = ["Eusoff Hall": '10 Kent Ridge Dr, Singapore 119242' , "Kent Ridge Hall": , "King Edward VII Hall", "Raffles Hall", "Sheares Hall", "Temasek Hall", "PGP House", "CAPT", "Tembusu", "RVRC", "RC4", "Cinnamon"]
stores = StoreData(menu.rests(), [1101780228,41345883])