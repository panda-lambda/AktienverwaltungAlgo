# testing:
# --add stock
# --add stock with same hash value
# --add stock with same name
# --add stock with same abbrev
#
# --del stock via abbrev
# --del stock via name
# --del stock that doesnt exits via abbrev
# --del stock that doesnt exits via name
#
# --import data via abbrev
# --import data via name
# --import data via abbrev that doesnt exist
# --import data via name that doesnt exist
# --import incorrect file
# --import data that is older via abbrev
# --import data that is older via name
# --overwrite data via abbrev
# --overwrite data via name
#
# --search by abbrev
# --search by name
# --search by non-existent abbrev
# --search by non-existent name
#
# --plot via name
# --plot via abbrev
# --plot via non exist name
# --plot via non exist abbrev
# --plot via name no data
# --plot via abbrev no data
#
# --save filled hash
#
# --load filled hash
# --load filled hash with wrong file

# import modules
import os
import csv
import pickle
import asciichartpy
from datetime import datetime

HASH_POWER = 10
DEBUG = 0
PLOT_HEIGHT = 30
MAX_COLLISION_COUNT = 1429
HASH_SIZE = 2003


class StockData:
    def __init__(self, name, abbrev, wkn):
        self.size = 30
        self.name = name
        self.abbrev = abbrev
        self.wkn = wkn
        # structure of price "Date	Open	High	Low	Close	Adj Close	Volume"
        self.prices = None

    def info(self):  # just for testing
        print(f"\tStock name:    {self.name}")
        print(f"\tStock abbr:    {self.abbrev}")
        print(f"\tStock wkn :    {self.wkn}")
        if self.prices is not None:
            print(f"\tlast cor. closing: {self.prices[0][5]}")  # last corrected closing value

    def info_data(self):  # just for testing
        print(self.name)
        print(self.prices)

    def plot_data(self):
        plot_csv_data(self.prices)


class StockHashTable:
    def __init__(self):
        self.size = 2003
        self.full_name_hash = self.size * [None]  # 2 hash for name and abbrev
        self.abbr_name_hash = self.size * [None]

    def info_hashtable(self):
        print(self.full_name_hash)
        print(self.abbr_name_hash)

    def hash_function(self, key):
        hash_value = 0
        power_decrement = HASH_POWER
        for char in key:
            hash_value += ord(char) ** power_decrement  # ord transforms into unicode/ascii integer
            if power_decrement > 1:  # char**10  +char**9 + .. +char**1
                power_decrement -= 1
        return hash_value % self.size  # unicode sum mod 2003

    def rehash_function(self, old_hash, index):
        return (old_hash + index ** 2) % self.size  # take quadratic probing in case of collision

    def get_new_name_index(self, name):
        hash_value = self.hash_function(name)
        if self.full_name_hash[hash_value] is None:
            return hash_value
        else:
            if self.full_name_hash[hash_value] == name:
                print("\nError: stock name already exists! in get_new_name_index")
            else:
                i = 1
                next_slot = self.rehash_function(hash_value, i)
                while self.full_name_hash[next_slot] is not None and self.full_name_hash[
                    next_slot].name != name and next_slot < MAX_COLLISION_COUNT:
                    i += 1
                    next_slot = self.rehash_function(hash_value, i)
                if self.full_name_hash[next_slot] is None:
                    return next_slot  # self.data[next_slot] = value
                elif self.full_name_hash[next_slot].name != name:
                    print("\nError: stock name already exists!")
                    if DEBUG == 1:
                        print("in get_new_name_index")
                else:
                    print("\nError: no more space for stock!")

    def get_existing_name_index(self, name):
        hash_value = self.hash_function(name)
        if self.full_name_hash[hash_value] is not None:
            if self.full_name_hash[hash_value].name == name:
                return hash_value
        else:
            i = 1
            next_slot = self.rehash_function(hash_value, i)
            # order important-> short circuit
            while self.full_name_hash[next_slot] is not None and self.full_name_hash[
                next_slot].name != name and next_slot < MAX_COLLISION_COUNT:
                i += 1
                next_slot = self.rehash_function(hash_value, i)
            if self.full_name_hash[next_slot] is not None and self.full_name_hash[next_slot].name == name:
                return next_slot
        return None

    def get_new_abbrev_index(self, abbrev):
        try:
            abbrev_index = self.hash_function(abbrev)
            if self.abbr_name_hash[abbrev_index] is None:
                return abbrev_index
            else:
                if self.abbr_name_hash[abbrev_index] == abbrev:
                    print("\nError: abbreviation already exists!")
                else:
                    i = 1
                    next_slot = self.rehash_function(abbrev_index, i)
                    while self.abbr_name_hash[next_slot] is not None and self.abbr_name_hash[
                        next_slot] != abbrev and next_slot < MAX_COLLISION_COUNT:
                        i += 1
                        next_slot = self.rehash_function(abbrev_index, i)
                    if self.full_name_hash[next_slot] is None:
                        return next_slot  # self.data[next_slot] = value
                    elif self.abbr_name_hash[next_slot] == abbrev:
                        print("\nError: abbreviation already exists!")
                        return None
                    else:
                        print("\nError: no space for new stock!")
                        return None
        except Exception as e:
            print("Error in get new abbrev index: ")
            print(e)

    def check_abbrev_equality(self, abbrev_index, abbrev):
        if abbrev_index is not None:
            stock_name = self.abbr_name_hash[abbrev_index]  # get stock name
            if stock_name is not None:
                # print("stock name ")
                # print(stock_name)
                stock_name_index = self.get_existing_name_index(stock_name)  # get stockname index in full name hash
                # print("stock index" + str(stock_name_index))
                if self.full_name_hash[stock_name_index] is not None:  # if that index has an object
                    found_abbrev = self.full_name_hash[stock_name_index].abbrev  # get the object's abbrev
                    if found_abbrev == abbrev:  # check if the abbrev and object's abbrev match
                        return abbrev_index
        return None

    def get_existing_abbrev_index(self, abbrev):
        # print("in get exist abbrev1")
        abbrev_index = self.hash_function(abbrev)  # get index where we expect the abbrev
        # print("in get exist abbrev2")
        if abbrev_index is not None:
            # check if the index leads to the correct name and then to the correct stock.abbrev value
            # print("in get exist abbrev3")
            found_abbrev = self.check_abbrev_equality(abbrev_index, abbrev)
            if found_abbrev is not None:
                return abbrev_index
            # in case there is no object or the object's abbrev does not match
            else:
                i = 1
                # print("in get exist abbrev4")
                next_slot = self.rehash_function(abbrev_index, i)
                # helper(self)
                while found_abbrev is None:
                    i += 1
                    if i > MAX_COLLISION_COUNT:
                        break
                    next_slot = self.rehash_function(abbrev_index, i)
                    found_abbrev = self.check_abbrev_equality(next_slot, abbrev)
                if self.check_abbrev_equality(next_slot, abbrev) is not None:
                    # print("abbrev found at" + str(next_slot))
                    return next_slot
                return None
        print("\nError: abbreviation not found! ")
        if DEBUG == 1:
            print("get_exisiting_abbrev_index")
        return None

    def insert_stock_name(self, name, abbrev, wkn):
        if type(name) == "" or abbrev == "" or wkn == "":
            print("\nError: you need to enter all three values!")
            return
        name_already_exists = self.get_existing_name_index(name)
        abbrev_already_exists = self.get_existing_abbrev_index(abbrev)
        # check if already exists
        if name_already_exists is None and abbrev_already_exists is None:
            try:
                hash_abbrev_index = self.get_new_abbrev_index(abbrev)
                hash_name_index = self.get_new_name_index(name)
                # create stock and fill name data
                stock = StockData(name, abbrev, wkn)
                self.full_name_hash[hash_name_index] = stock
                self.abbr_name_hash[hash_abbrev_index] = name
                # print(" stock successfully inserted at index: " + str(hash_name_index))
                assert self.full_name_hash[hash_name_index] is not None
            except Exception as e:
                print(e)
            print("\nSuccess!\n\n********* INFO*************")
            self.full_name_hash[hash_name_index].info()
        else:
            print("\nError: name or abbreviation already exists!")

    def insert_data_via_name(self, name_to_add_data, data):
        assert name_to_add_data is not None
        assert data is not None
        # check if data exists, if not insert data
        name_index_to_add_data = self.get_existing_name_index(name_to_add_data)
        if name_index_to_add_data is not None:
            # print(name_index_to_add_data)
            if self.full_name_hash[name_index_to_add_data] is not None:
                # no data bound
                if self.full_name_hash[name_index_to_add_data].prices is None:
                    self.full_name_hash[name_index_to_add_data].prices = data
                    if self.full_name_hash[name_index_to_add_data].prices is not None:
                        print("\nData successfully bound to stock!")
                else:
                    # check if date is more recent
                    existing_date = datetime.strptime(self.full_name_hash[name_index_to_add_data].prices[0][0],
                                                      '%Y-%m-%d')
                    new_date = datetime.strptime(data[0][0], '%Y-%m-%d')
                    if existing_date >= new_date:
                        print("\nError: imported data is older or equal!")
                    else:
                        self.full_name_hash[name_index_to_add_data].prices = data
                        print("\nData successfully replaced!")
            else:
                print("\nError: no stock with this name found!")
        else:
            print("\nError: no stock with this name found! ")
            if DEBUG == 1:
                print("in inser_data_via name")

    def insert_data_via_abbrev(self, abbrev_to_add_data, data):
        # get name for abbrev
        abbrev_index_to_add_data = self.get_existing_abbrev_index(abbrev_to_add_data)
        if abbrev_index_to_add_data is not None:
            name_to_add_data = self.abbr_name_hash[abbrev_index_to_add_data]
            # print(name_to_add_data)
            self.insert_data_via_name(name_to_add_data, data)
        else:
            print("\nError: stock with this abbreviation does not exist!")
            if DEBUG == 1:
                print("in insert_data_via_abbrev")

    def search_by_name(self, name):
        assert name is not None
        # print("in search_by_name")
        try:
            hash_name_index = self.get_existing_name_index(name)
            if hash_name_index is not None:
                # print("index gefunden an ")
                # print(hash_name_index)
                try:
                    print("\n\n********* INFO*************")
                    self.full_name_hash[hash_name_index].info()
                except Exception as e:
                    print(e)
            else:
                print("\nError: no stock with this name was found! ")
        except Exception as e:
            print("ERROR in search by name ")
            print(e)

    def search_by_abbrev(self, abbrev):
        assert abbrev is not None
        try:
            abbrev_index = self.get_existing_abbrev_index(abbrev)

            if abbrev_index is not None:
                self.search_by_name(self.abbr_name_hash[abbrev_index])
            else:
                print("\nError: abbreviation not found!")
        except Exception as e:
            print("Error in search abbrev ")
            print(e)

    def plot_via_name(self, stock_name):
        assert stock_name is not None
        name_index_to_plot = self.get_existing_name_index(stock_name)
        if name_index_to_plot is not None:
            # print(name_index_to_plot)
            if self.full_name_hash[name_index_to_plot] is not None:
                if self.full_name_hash[name_index_to_plot].prices is not None:
                    self.full_name_hash[name_index_to_plot].plot_data()
                else:
                    print("\nError: no data imported for that stock!\n\n")
            else:
                print("\nError: no stock with that name found!\n\n")
        else:
            print("\nError: stock not found! \n\n")
            if DEBUG == 1:
                print("in plot via name")

    def plot_via_abbrev(self, abbrev):
        abbrev_index_to_plot = self.get_existing_abbrev_index(abbrev)
        if abbrev_index_to_plot is not None:
            name_to_plot = self.abbr_name_hash[abbrev_index_to_plot]
            if name_to_plot is not None:
                self.plot_via_name(name_to_plot)
        else:
            print("\nError: stock with this abbreviation does not exist!")
            if DEBUG == 1:
                print("in plot_via_abbrev")

    def export_hash(self, file_name):
        try:
            # just for checking what was in the hash list
            my_list = self.full_name_hash
            if my_list.count(None) == len(my_list):
                print("\nError: nothing to export")
                return
            for i in range(len(my_list)):
                if my_list[i] is not None:
                    print("exported:")
                    print(f"Index {i} contains a value: {my_list[i]}")
            my_list = self.abbr_name_hash
            for i in range(len(my_list)):
                if my_list[i] is not None:
                    print("exported:")
                    print(f"Index {i} contains a value: {my_list[i]}")
            # write file in w: write, b:binary
            with open(file_name + ".pickle", "wb") as f:
                save_object = (self.full_name_hash, self.abbr_name_hash)  # use tuple
                pickle.dump(save_object, f)  # pickle.dump(self.full_name_hash, f)
        except Exception as e:
            print(e)

    def delete_via_name(self, stock_name):
        # print("in delete via name")
        assert stock_name is not None
        name_index_to_del = self.get_existing_name_index(stock_name)
        if name_index_to_del is not None and self.full_name_hash[name_index_to_del] is not None:
            get_abbrev_to_del = self.full_name_hash[name_index_to_del].abbrev
            get_abbrev_index_to_del = self.get_existing_abbrev_index(get_abbrev_to_del)
            get_name_index_to_del = self.get_existing_name_index(stock_name)
            if get_abbrev_index_to_del is not None and get_name_index_to_del is not None:
                try:
                    del self.full_name_hash[get_name_index_to_del]
                    self.abbr_name_hash[get_abbrev_index_to_del] = None
                    if self.full_name_hash[get_name_index_to_del] is None and self.abbr_name_hash[
                        get_abbrev_index_to_del] is None:
                        print(
                            "\nDeletion was successful!")  # not sure if needed.  # self.full_name_hash[get_name_index_to_del] = None  # self.abbr_name_hash[get_abbrev_index_to_del] = None
                except Exception as e:
                    print("Error")
                    print(e)
            else:
                print("\nError stock not found! ")
                if DEBUG == 1:
                    print("in delete via name")
        else:
            print("\nError: stock with this name not found! ")
            if DEBUG == 1:
                print("in delete_via_name")

    def delete_via_abbrev(self, abbrev):
        abbrev_index_to_del = self.get_existing_abbrev_index(abbrev)
        if abbrev_index_to_del is not None:
            name_to_del = self.abbr_name_hash[abbrev_index_to_del]
            if name_to_del is not None:
                self.delete_via_name(name_to_del)
        else:
            print("\nError: stock with this abbreviation does not exist!")


#########################################other functions################################################
def get_date(row):
    # data string from first row converted into datetime object for comparison
    return datetime.strptime(row[0], '%Y-%m-%d')


def get_csv_data(file_name):
    try:
        with open(file_name + ".csv", newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            next(reader)  # ignore first row (heading)
            sorted_reader = sorted(reader, key=get_date, reverse=True)
            recent_entries = sorted_reader[:30]
            return recent_entries
    except Exception as e:
        if DEBUG == 1:
            print(e)
            directory = os.getcwd()
            print(directory)
        return -1


def plot_csv_data(recent_entries):
    adjusted_closing = []
    for row in recent_entries:
        adjusted_closing.insert(0, float(row[5]))  # reverse order again, so last is most recent
    chart = asciichartpy.plot(adjusted_closing, {'colors': [asciichartpy.magenta], 'height': PLOT_HEIGHT})
    print(chart)
    print(
        f"\nEarliest:    {recent_entries[-1][0]} with {adjusted_closing[0]} to\nmost recent: {recent_entries[0][0]} with {adjusted_closing[-1]}\n\n")


def import_serialized(file_name, stock_hash_table):
    # open in binary mode = b, open in read mode = r
    try:
        with open(file_name + ".pickle", "rb") as f:
            imported = pickle.load(f)
        try:
            stock_hash_table.full_name_hash = imported[0]  # replaces both hash tables!!
            stock_hash_table.abbr_name_hash = imported[1]
            fullname_list = imported[0]
            print("The following stocks names were imported:\n")
            for i in range(len(fullname_list)):
                if fullname_list[i] is not None:
                    print(f"{fullname_list[i].name} |", end=" ")
            print("\n")
        except Exception as e:
            print(e)
    # test if file was imported correctly
    except Exception as e:
        print("\nERROR: " + file_name + ".pickle import failed!")
        if DEBUG == 1:
            print(e)


def helper(stock_hash_table):
    print("\n+++++++checking for content++++++++")
    my_list = stock_hash_table.full_name_hash
    my_list_abbrev = stock_hash_table.abbr_name_hash
    try:
        for i in range(len(my_list)):
            if my_list[i] is not None:
                print(f"\n In fullname hash for {my_list[i].name}")
                print(f"\tfull name Index {i} contains a value: {my_list[i]}")
            if my_list_abbrev[i] is not None:
                print(f"\tabbrev Index {i} contains a value: {my_list_abbrev[i]}")
        print("************checked for content*******\n")
    except Exception as e:
        if DEBUG == 1:
            print(e)


def input_logic(user_input, stock_hash_table):
    try:
        int_user_input = (int(user_input))
        if int_user_input < 1 or int_user_input > 9:
            print("\n\tPlease enter a number between 1 and 8!\n\n")
        else:
            if int_user_input == 1:
                print("\n\t1.ADDING A STOCK")
                stock_name = input("\tName: ")
                stock_abbrev = input("\tAbbrev (must be UPPERCASE): ")
                stock_wkn = input("\tWKN: ")
                try:
                    stock_hash_table.insert_stock_name(stock_name, stock_abbrev, stock_wkn)
                    if DEBUG == 1:
                        helper(stock_hash_table)  # check if import worked
                except Exception as e:
                    print(e)
            elif int_user_input == 2:
                print("\n\t2.DELETING A STOCK")
                del_stock = input("\tEnter name or abbreviation of stock to be deleted: ")
                if del_stock is not None:
                    if del_stock.isupper():  # check if whole word is uppercase=> abbrev
                        stock_hash_table.delete_via_abbrev(del_stock)
                    else:
                        stock_hash_table.delete_via_name(del_stock)
            elif int_user_input == 3:
                print("\n\t3.IMPORTING DATA")
                stock_to_add_data = input("\tEnter stock name/abbreviation: ")
                file_name = input("\tEnter file name without .csv (same folder as .exe): ")
                data = get_csv_data(file_name)
                if data == -1:
                    print("\nError: import of " + file_name + ".csv failed.")
                else:
                    print("\nData was successfully read!")
                    if stock_to_add_data is not None:
                        if stock_to_add_data.isupper():  # check if whole word is uppercase=> abbrev
                            stock_hash_table.insert_data_via_abbrev(stock_to_add_data, data)
                        else:
                            stock_hash_table.insert_data_via_name(stock_to_add_data, data)
            elif int_user_input == 4:
                print("\n\t4.SEARCH CLOSING STOCK VALUE")
                search_input = input("\tEnter name or abbreviation to search: ")
                if search_input is not None:
                    if search_input.isupper():
                        stock_hash_table.search_by_abbrev(search_input)
                    else:
                        stock_hash_table.search_by_name(search_input)
            elif int_user_input == 5:
                print("\n\t5.PLOTTING LAST 30 CLOSING VALUES")
                plot_stock = input("\tEnter name or abbreviaton of stock to plot: ")
                if plot_stock is not None:
                    if plot_stock.isupper():  # check if whole word is uppercase=> abbrev
                        stock_hash_table.plot_via_abbrev(plot_stock)
                    else:
                        stock_hash_table.plot_via_name(plot_stock)
            elif int_user_input == 6:
                print("\n\t6.SAVING TO .PICKLE FILE")
                print("\tExporting bytestream file, will be saved in same folder as application.")
                file_name = ""
                while file_name == "":
                    file_name = input("\tEnter file name (without .pickle) : ")
                stock_hash_table.export_hash(file_name)
            elif int_user_input == 7:
                print("\n\t7.LOADING .PICKLE FILE")
                print("\tLoading bytestream file, warning! will overwrite currently saved stocks!!")
                file_name = input("\tEnter file name (without .pickle, same folder) : ")
                import_serialized(file_name, stock_hash_table)
            elif int_user_input == 8:
                print("\n\t8.WARNING: ALL UNSAVED DATA WILL BE DELETED!")
                exit_answer = input("\n\tDo you want to proceed? (y | n): ")
                while (1):
                    if exit_answer == 'y':
                        int_user_input = 10
                        print("\n\nYou terminated the application.")
                        break
                    elif exit_answer == 'n':
                        print("\n\n You canceled exiting the application.")
                        int_user_input = 10
                        break
                    else:
                        exit_answer = input("\tDo you want to proceed? (y | n): ")
            elif int_user_input == 9 and DEBUG == 1:
                helper(stock_hash_table)
    except Exception as e:
        if DEBUG == 1:
            print("\n\nError in input logic:")
            print(e)
        print("\n\tPlease enter a valid number!\n")
        int_user_input = 0
    return int_user_input


# main loop

user_input = None
stock_hash_table = StockHashTable()  # create hash table
while user_input != 10:
    os.system("cls")  # will clear screen, but not in PyCharm due to PyCharm's emulation, os.system("clear") for UNIX.
    print("\n\tSTOCK MANAGEMENT MENU")
    # print("'microsoft' is index 982")
    print("\t1. ADD    | a stock with name, abbreviation and WKN.")
    print("\t2. DEL    | a stock gets deleted.")
    print("\t3. IMPORT | data for one particular stock is imported and saved. ")
    print("\t4. SEARCH | get most recent stock price value of chosen stock.")
    print("\t5. PLOT   | get graphical display of course development of the last 30 trading days")
    print("\t6. SAVE   | export the two hash tables into bytestream file.")
    print("\t7. LOAD   | import the two hash tables from bytestream file")
    print("\t8. QUIT   | exit the program. WARNING: All unsaved data will be lost!")
    if DEBUG == 1:
        print("\t9. INFO   | print all entries in hashtable")
    user_input = input("\tPlease enter a number between 1 and 8: ")
    user_input = input_logic(user_input, stock_hash_table)
    if user_input == 10:
        break
    input("Press Enter to continue...")
#not clear if the for loop is necessary
for i in stock_hash_table.full_name_hash:
    del i
del stock_hash_table

