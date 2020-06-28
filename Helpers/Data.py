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

        spl_to_str = lambda s : np.asarray(s.split(","), dtype = np.unicode_).astype(str) if type(s) is str else s
        spl_to_float = lambda s : np.asarray(s.split(","), dtype = np.float64).astype(float) if type(s) is str else s
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
        restaurant: Restaurant Name
        ID: Object ID
        Option: (int, list, list) 
            0 gives you the base price
            1 gives you the list of addon prices of option 1
            2 gives you the list of addon prices of option 2
        """
        #check if key exists
        if ID in (self.price[restaurant].index):
            if option == 0:
                return self.price[restaurant].iloc[:,option].loc[ID]
            elif option == 1:
                return self.price[restaurant].iloc[:,option].loc[ID]
            elif option == 2:
                return self.price[restaurant].iloc[:,option].loc[ID]    
        else:
            return print("Error: ID does not exist")
    
    def item(self, restaurant, ID, option = 0):
        """Returns the name of an object
        restaurant: (str) Restaurant Name
        ID: (int) Object ID
        Option: (int, list, list)
            0 gives you the item's name
            1 gives you the list of addon names of option 1
            2 gives you the list of addon names of option 2
        """
        
        #check if key exists
        if ID in (self.food[restaurant].index):
            if option == 0:
                return self.food[restaurant].iloc[:,option].loc[ID]
            elif option == 1:
                return self.food[restaurant].iloc[:,option].loc[ID]
            elif option == 2:
                return self.food[restaurant].iloc[:,option].loc[ID]
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
            return self.food[restaurant].index.to_numpy()
        if data == 1:
            # Print Food [col]
            return self.food[restaurant].iloc[:,col].to_numpy()
        if data == 2:
            # Print Price [col]
            return self.price[restaurant].iloc[:,col].to_numpy()
    
    def rests(self):
        return self.restaurants

# class StoreData:
#     def __init__(self, list_of_stores = np.empty(0, dtype=str), list_of_ids = np.empty(0, dtype=str)):
#         self.df = pd.DataFrame(
#             {'Store': list_of_stores,
#              'ID:': list_of_ids,
#              'Avail': np.full(len(list_of_stores), False)})
    
#     def add(self, store, id):
#         self.df = self.df.append(
#             {'Store': store,
#              'ID:': id,
#              'Avail': False}, ignore_index = True)
#         return self.df

#     def avail(self, id):
#         self.df

# def main():
#     storedata = StoreData().add("hello", 9)

menu = Menu("Menu.xlsx")
# main()