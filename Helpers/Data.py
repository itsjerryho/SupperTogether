import pandas as pd
import numpy as np

class Menu:
    def __init__(self, filename):
        self.filename = filename
        self.df = pd.read_excel(filename, sheet_name = None, index_col = 0)
        self.food = {}
        self.price = {}
        # List of restaurants
        self.restaurants = list(self.df.keys())

        spl_to_str = lambda s : np.asarray(s.split(",")).astype(str) if type(s) is str else s
        spl_to_float = lambda s : np.asarray(s.split(",")).astype(float) if type(s) is str else s
        # Process data
        for r in self.restaurants:
            r_data = self.df[r]
            r_data.iloc[:,[2,4]] = r_data.iloc[:,[2,4]].applymap(spl_to_str)
            r_data.iloc[:,[3,5]] = r_data.iloc[:,[3,5]].applymap(spl_to_float)
            # Item data frame

            #Price data frame
            self.price[r] = pd.merge(pd.merge(r_data.iloc[:,1], r_data.iloc[:,3], on = 'OrderID'), r_data.iloc[:,5], on = 'OrderID')

            self.food[r] = pd.merge(pd.merge(r_data.iloc[:,0], r_data.iloc[:,2], on = 'OrderID'), r_data.iloc[:,4], on = 'OrderID')
    
    def cost(self, restaurant, ID, option = 0):
        """Returns the cost an object
        restaurant: (str) Restaurant Name
        ID: (int|tuple) Object ID
            if ID is tuple, method will add all the cost
        Option: (int, list, list) 
            0 gives you the base price
            1 gives you the list of addon prices of option 1
            2 gives you the list of addon prices of option 2
        """
        if type(ID) is tuple:
            ans = [None]*len(ID)
            id = ID[0]
            ans[0] = self.price[restaurant].iloc[:,0].loc[id] if id is not None else 0
            ans[1] = self.price[restaurant].iloc[:,1].loc[id][int(ID[1])] if ID[1] is not None else 0
            ans[2] = self.price[restaurant].iloc[:,2].loc[id][int(ID[2])] if ID[2] is not None else 0
            return sum(ans)
        
        #check if key exists
        if ID in (self.price[restaurant].index):
            if option == 0:
                output = self.price[restaurant].iloc[:,option].loc[ID]
            elif option == 1:
                output = self.price[restaurant].iloc[:,option].loc[ID]
            elif option == 2:
                output = self.price[restaurant].iloc[:,option].loc[ID]
            
            return output if not np.any(np.isnan(output)) else None

        else:
            return print("Error: ID does not exist")
    
    def item(self, restaurant, ID, option = 0):
        """Returns the name of an object
        restaurant: (str) Restaurant Name
        ID: (int|tuple) Object ID
            if ID is tuple, method will concatenate all together
        Option: (int, list, list)
            0 gives you the item's name
            1 gives you the list of addon names of option 1
            2 gives you the list of addon names of option 2
        """
        if type(ID) is tuple:
            ans = [None]*len(ID)
            id = ID[0]
            ans[0] = self.food[restaurant].iloc[:,0].loc[id] if id is not None else ""
            ans[1] = self.food[restaurant].iloc[:,1].loc[id][int(ID[1])] if ID[1] is not None else ""
            ans[2] = self.food[restaurant].iloc[:,2].loc[id][int(ID[2])] if ID[2] is not None else ""
            return ' '.join(ans)
        else:
            #check if key exists
            if ID in (self.food[restaurant].index):
                if option == 0:
                    output = self.food[restaurant].iloc[:,option].loc[ID]
                elif option == 1:
                    output = self.food[restaurant].iloc[:,option].loc[ID]
                elif option == 2:
                    output = self.food[restaurant].iloc[:,option].loc[ID]
                

                # output can be either array or string
                if type(output) is np.float64:
                    return output if not np.isnan(output) else None
                else:
                    return output
            else:
                return print("Error: ID does not exist")

    def listing(self, restaurant, data, col=0):
        """ Gives you a list of data
        restaurant: (str) Restaurant Name
        data: (int) Select which data you want
            0: Object IDs
            1: Item names
            2: prices
        col: (int, list, list) select which option you want
            0: Main
            1: Option 1
            2: Option 2
        """
        if data == 0:
            # Print OrderID
            output = self.food[restaurant].index.to_numpy().tolist()
        if data == 1:
            # Print Food [col]
            output = self.food[restaurant].iloc[:,col].tolist()
        if data == 2:
            # Print Price [col]
            output = self.price[restaurant].iloc[:,col].tolist()

        if type(output[0]) is float:
            if np.any(np.isnan(output)):
                # if any output is Nan, return None
                return None
            else:
                return output
        else:
            return output
    
    def rests(self):
        return self.restaurants

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
stores.df.to_excel("Stores.xlsx")

def Test() :
    r1 = "Ah Beng Drink"
    r2 = "Ah Lian Food"
    # Test individual items
    # None Values
    print(menu.cost(r2, "A1", 2)) # return cost A1 option 2 = None
    print(menu.item(r2, "A1", 2)) # return cost A1 option 2 = None
    print(menu.listing(r2, 1, 2)) # return list of names, option 2 = [None]
    print(menu.listing(r2, 2, 2)) # return list of cost, option 2 = [None]


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