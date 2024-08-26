# SDTP Examples
This repo hosts examples of using the Global Data Plane (Simple Data Markup Language, Simple Data Query Language, and Simple Data Transfer Protocol) to host, publish, and query data.  
Each subdirectory (except client) has server code, to show how to host data to query it.  _It should be noted that the Simple Data Markup Language and Simple Data Query Language do not require network mediation!_ The SDTP package can be used entirely client-side to have a fast interface to query data.

The client subdirectory contains code to query the simple-table-example server or the db-example server.  Since these servers serve identical data from different sources, the same client code is used to query both of them. _The Global Data Plane is completely independent of the storage systems used to house data, due to the *Data Equivalence Principle*_.  The fact that the same code queries both the db-example and the simple-table-example is the demonstration of that.


