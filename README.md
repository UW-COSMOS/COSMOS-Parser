### Setup with Python3.6
1. Install dependencies
	* Mac:
		```bash 
		make install-mac
		```

	* Linux:
		```bash 
		make install-linux
		```
2. Create a database in PostgreSQL and configure the database connection string in ```Makefile``` accordingly.

3. Place all html source files in ```data/html/files``` (also configurable in the ```Makefile```). **PLEASE MAKE SURE THIS FOLDER ONLY CONTAINS THE HTML FILE BUT NOTHING ELSE.**

### Usage
Consume all files in ```data/html/files``` and populate information in the database
```
make
```

