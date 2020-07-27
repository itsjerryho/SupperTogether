import pandas as pd
import numpy as np


cat_1 =  "Cat_1"

class Menu:
    def __init__(self, filename):
        self.filename = filename
        self.df = pd.read_excel(filename, sheet_name = None, index_col = 0)
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
            self.cat[r] = r_data.iloc[:,0]

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
        return ' '.join(ans)

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
        return list(dict.fromkeys(self.cat[r].dropna()))
    
    def cat_subset(self, r, cat):
        subset = self.cat[r].loc[self.cat[r] == cat]
        return subset.index.to_numpy().tolist()

        
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

menu = Menu("Menu.xlsx")
stores = StoreData(menu.rests(), [1101780228,41345883])

print(menu.list_of_cat("Ah Lian Food"))
# print(menu.list_of_costs("Ah Lian Food",menu.cat_subset("Ah Lian Food", "Western")))


def Test() :
    r1 = "Ah Beng Drink"
    r2 = "Ah Lian Food"
    # Test individual items
    # None Values
    print(menu.list_of_cost_options(r2, 0, 2)) # return cost A1 option 2 = None
    print(menu.list_of_item_options(r2, 0, 2)) # return cost A1 option 2 = None
    print(menu.listing(r2, 1, 2)) # return list of names, option 2 = None
    print(menu.listing(r2, 2, 2)) # return list of cost, option 2 = None
    print(menu.list_of_cost_options(r2, 0, 0))

    # Not None
    print(menu.listing(r2, 0, 0)) # return ID
    print(menu.listing(r2, 1, 0)) # return list of items, option 0
    print(menu.listing(r2, 2, 0)) # reutrn list of items, option 1

    # Test combination
    # W/ None
    print(menu.item(r2, ("A1", 0, None)))
    print(menu.cost(r2, ("A1", 0, None)))

    # w/o None
    print(menu.item("Ah Beng Drink", ("A1", 0, 0)))

def Simulation():
    # Simulation
    # get list, choose item
    r2 = "Ah Lian Food"
    ans = [None]*3
    print(menu.listing(r2, 0))
    print(menu.listing(r2, 1))
    print(menu.listing(r2, 2))

    # Choose "A2"
    ans[0] = "A2"
    print(menu.item(r2, ans[0], 1))
    print(menu.cost(r2, ans[0], 1))

    # see if still got options
    ans[1] = 0
    if menu.item(r2, ans[0], 2) is None:
        print(menu.item(r2,tuple(ans)))
        print(menu.cost(r2,tuple(ans)))

# Test()
# Simulation()