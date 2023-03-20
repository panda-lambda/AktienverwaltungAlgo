# AktienverwaltungAlgo
*The application was created in the summer semester 2022 in the course algorithsm and datastructures at the UAS Vienna(FH Technikum Wien)*

The task was to implement a simple console application where a user can save, plot and store stock data using a self-written hashtable to store the data. 
The application uses a simple hashing algorithm with `n^^10+n^^9+...n^^1` and quadratic probing as collision handling. 

It is possible to use the full stock name or an abbreviation,  abbrevations are stored in a second hashmap which contains the full name of the stock. 
In order to import .csv data, one should use [finance.yahoo](https://de.finance.yahoo.com/quote/MSFT/history?p=MSFT) and download some historic data. The application saves up to 30 rows of data and checks if the imported data is more recent than the existing one. 


![Plotting the data](https://raw.githubusercontent.com/panda-lambda/AktienverwaltungAlgo/main/aktienverwaltung_plot.png)
