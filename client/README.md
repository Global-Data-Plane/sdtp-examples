# Simple Table Client Example
This directory contains two clients for the Simple  Table SDTP example.  Both clients are expressed as Jupyter Notebooks (for experimentation and interactive work) and as simple Python scripts (for people who don't have Jupyter installed).  The clients are both very bare-bones: they are designed to permit experimentation and extension.

## simple_table_example

The `simple_table_example` has no library dependencies other than `requests`, the standard Python http requests library.  To use it, first, start `app.py` in the server directory, then change the cell `server_url = 'http://localhost:5001'` to point to the URL of the local server.  The '/' and '/help' routes on the server send a JSON explanation of the available routes and thei functions.

The Python file `simple_table_example.py` has the same functionality, but in a simple Python program.  The Notebook is encouraged for exploration and documentation, and the Python file is provided as a convenience for those who do not have Jupyter installed.

## SDTP_Simple_Table
Though by design the Simple Data Transfer Protocol requires _no_ client-side libraries other than any HTTP/S library to make requests and JSON library to read the responses, the Simple Data Transfer Library package used client-side can greatly simplify the client code.  The library has a `RemoteSDMLTable` class designed to allow SDTP servers to serve tables hosted on other SDTP servers, and, used client-side, this offers a convenient way to query tables hosted on the server without direct reference to the requests library or explicitly forming the queries.  It is used as follows:

### initialization: `RemoteSDMLTable(<table_name>, <schema>, <server_url>)`

`<table_name>` is the name of the table _on the server_.
`<schema>` is the schema of the table, a list of objects of the form `{"name": <column_name>, "type": <column_type>}`, which must agree with the schema on the server  both in names and order.
`<server_url>` is the URL of the server.

### Issuing column queries
| API Call | REST Equivalent | Function | 
|----------|-----------------|----------|
| `RemoteSDMLTable.all_values(column_name)` | `get_all_values?table_name=<table_name>&column_name=<column_name>` | Get all the distinct values in `<column_name>` |
| `RemoteSDMLTable.range_spec(column_name)` | `get_range_spec?table_name=<table_name>&column_name=<column_name>` | Get all the  min and max values in `<column_name>` as an ordered list |
| `RemoteSDMLTable.get_column(column_name)` | `get_column?table_name=<table_name>&column_name=<column_name>` | Get the column `<column_name>` as a list |
|--------------|-----------------------------|-------------------|

Note the returns from the API calls are _identical_ to the REST requests.

### Row filters
The equivalent to the REST request `get_filtered_rows` with the json POST body `{table: <table_name>, columns:<column_names>, filter_spec:<filter_spec>` is the call `RemoteSDMLTable.get_filtered_rows(filter_spec, column_names)`, where the default for `filter_spec` is `None` and the default for `column_names` is `[]`.
