# Simple Table Example (SQLite)
This directory hosts the Simple Table Example for the Simple Data Transfer Protocol.  The server serves the same data as in the Simple Table Example; however, it does so from a SQLite database, so the purpose of this example is to show how to server tables from a database.  _It is important to note that the same queries over the same tables are supported by this example and the Simple Table Example, and the results will be identical._

The `presidential_vote.db` file is the SQLite file containing the database.  The six SQL files to build this database are in the `sql` subdirectory.  These are only included for reference; they aren't needed to load the data so long as the `presidential_vote.db` file is present.

The module `sqlite_interface.py` contains the classes required to interface between a SQLite database and the Global Data Plane.  There are two major classes, `SQLiteConnection` and `SDMLSQLiteTable`.  A `SQLiteConnection` automates the execution of  queries of the DB and implements the `REGEXP` operator.  An `SDMLSQLiteTable` implements the SDML Table interface over SQLite data.

As a note, the `sqlite_interface.py` code should migrate to an sdtp-extensions package once that is robust.

