from sdtp import  SDMLTable,  jsonifiable_column
from sdtp import  SDML_NUMBER, SDML_BOOLEAN, SDML_DATE, SDML_DATETIME, SDML_TIME_OF_DAY, SDML_STRING
import sqlite3
import re
import datetime

def _sqlite_regex_match(pattern, text):
    # A utility which returns True if pattern matches any part of the given text.  
    # this is to be a callback for SQLite to define a regexp expression for the SQL REGEXP 
    # operator
    return re.search(pattern, text) is not None

class SQLiteConnection:
    '''
    Interface to a SQLite database.  Creates the connection, defines the regex function,
    and executes SQL queries on the DB, returning the results in a list.
    Arguments:
        db: name of the database file
    '''
    def __init__(self, db):
        self.connection = sqlite3.connect(db, check_same_thread = False)
        self.connection.create_function("REGEXP", 2, _sqlite_regex_match)
        self.cursor = self.connection.cursor()

    def execute_query_return_result(self, sql_query):
        '''
        Execute a SQL query and return the result, from which a fetchone() or fetchall() can be executed.
        Provided primarily for testing and debugging purposes.
        '''
        return self.cursor.execute(sql_query)

    def execute_query_return_list(self, sql_query, return_one = False):
        '''
        Execute the SQL query.  If fetchone is true, return only one result.  Otherwise return all.  This
        returns either a list or a list of lists, depending on the query

        '''
        result = self.execute_query_return_result(sql_query)
        return result.fetchone() if return_one else result.fetchall()


'''
Translation methods from atomic values in SDQL/SDML/ISO Format to SQLite SQL.  The translations are in 
this table:

| SQLite Type | SDQL Type           | SQLite Format                    | SDQL Format                |
|-------------|---------------------|----------------------------------|----------------------------|
| INT         | SDML_NUMBER         |  nnn                             | nnnn.nn                    |
| REAL        | SDML_NUMBER         |  nnn.nn                          | nnnn.nn                    |
| INT         | SDML_BOOLEAN        |  1/0                             | true/false                 |
| TEXT        | SDML_STRING         |  'ssssssssss'                    | "ssssssss"                 |
| DATETIME    | SDML_DATETIME       |  datetime('YYYY-MM-DD hh:mm:ss') | "YYYY-MM-DDThh:mm:ss.nnn"  |
| DATE        | SDML_DATE           |  date('YYYY-MM-DD')              | "YYYY-MM-DD"               |
| TIME        | SDML_TIME_OF_DAY    |  time('hh:mm:ss')                | "hh:mm:ss.nnn"             |
|-------------|---------------------|----------------------------------|----------------------------|
Other types, e.g. VARCHAR, format as string
'''
def datetime_to_sql(isoformat_datetime):
  '''
  Convert an ISO Format Datetime "YYYY-MM-DDThh:mm:ss.nnn" 
  to a SQLite datetime ("datetime('YYYY-MM-DD hh:mm:ss')")
  Arguments:
     - isoformat_datetime: a datetime in iso format
  Returns:
     - a SQLite datetime
  '''
  # split into date and time
  as_list = isoformat_datetime.split('T')
  iso_date  = as_list[0]
  # If there is no time, the time is 00:00:00
  iso_time = as_list[1] if len(as_list) > 1 else '00:00:00'
  # Split off the subseconds -- SQLite doesn't support them
  sql_time = iso_time.split('.')[0]
  return f"datetime('{iso_date} {sql_time}')"

def date_to_sql(isoformat_date):
  '''
  Convert an ISO Format date "YYYY-MM-DD" 
  to a SQLite date ("date('YYYY-MM-DD')")
  Arguments:
     - isoformat_date: a date in iso format
  Returns:
     - a SQLite date
  '''
  return f"date('{isoformat_date}')"


def time_to_sql(isoformat_time):
  '''
  Convert an ISO Format time "hh:mm:ss.nnn" 
  to a SQLite time ("time(hh:mm:ss')")
  Arguments:
     - isoformat_time: a time in iso format
  Returns:
     - a SQLite time
  '''
  # Split off the trailing subseconds
  sql_time = isoformat_time.split('.')[0]
  return  f"time('{sql_time}')"

def translate_value_to_sql(value, sdml_type):
  '''
  Convert a value that is of type sdml_type to sql.  This uses the 
  matrix above to fill in the appropriate sql value, and utilizes the
  datetime, date, and time routines for those types
  Arguments:
     - value: the SDML value to convert
     - sdml_type: the type of the SDML value (one of SDML_BOOLEAN, SDML_STRING, SDML_NUMBER, SDML_DATETIME, SDML_DATE, SDML_TIME_OF_DAY)
  Returns:
     - The value in SQLite form (this plugs into a SQL statement, so it will always be a string)
  '''
  if sdml_type == SDML_BOOLEAN: return "1" if value else "0" # in SQLite, 1 is true, 0 is falst
  if sdml_type == SDML_STRING: return f"'{value}'" # add single quotes around strings
  if sdml_type == SDML_NUMBER: return f"{value}" # This will plug into a SQL statement, so convert a number to "number"
  if sdml_type == SDML_DATE: return date_to_sql(value) # convert a date
  if sdml_type == SDML_TIME_OF_DAY: return time_to_sql(value) # convert a time
  return datetime_to_sql(value) # convert a datetime

'''
Translation methods for results IN SQLite form to SDML -- the appropriate type if JSONIFY is false, a string if 
jsonify is True.  The only complexity if jsonify is true is putting the 'T' separator in a datetime.
Arguments:
     - value: the SQLite value to convert
     - sdml_type: the SDML type to convert to (one of SDML_BOOLEAN, SDML_STRING, SDML_NUMBER, SDML_DATETIME, SDML_DATE, SDML_TIME_OF_DAY)
     - jsonify: if true, convert to a jsonifiable form (primarily, ensure the datetime is converted properly).  Otherwise, convert to the appropriate data structure
  Returns:
     - The value in SDML form
'''

def translate_value_from_sql(value, sdml_type, jsonify = False):
  '''
  Translate a value which is returned from a SQLite query into the appropriate SDML type, as follows:
  | SQL Result | SDML Type        | Python type       | JSONifiable Type              |
  |------------|------------------|-------------------|-------------------------------|
  | 1/0 int    | SDML_BOOLEAN     | boolean           | boolean                       |
  | Real or Int| SDML_NUMBER      | float             | float                         |
  | String     | SDML_STRING      | str               | str                           |
  | Datetime   | SDML_DATETIME    | datetime.datetime | datetime string in iso format |
  | Date       | SDML_DATE        | datetime.date     | date string in iso format     |
  | Time       | SDML_TIME_OF_DAY | datetime. time    | time string in iso format     |
  |------------|------------------|-------------------|-------------------------------|
  
  Arguments:
    - value: the value to be translated
    - sdml_type: the type to translate to
    - jsonify: if true, return a value appropriate for jsonification; if false, return the appropriate Python type
  Returns:
    The corresponding Python value (see table)
  '''
  if sdml_type == SDML_BOOLEAN:
      # in both jsonify and non-jsonify cases, convert 1 to True and everything else to False
      return value == 1
  if jsonify:
      # if jsonify is true, and the type is not SDML_BOOLEAN (the only case which leads us here), the only
      # value NOT in ISO format (or JSON-ready type) is Datetime, because SQL uses a non-standard blank separator
      # between date and time (<date> <time) vs ISO <date>T<time>. So fix this, carefully
      if sdml_type == SDML_DATETIME:
          # Annoying SQLite separates date from time with a space, not 'T'
          # split off leading and trailing whitespace
          dt = value.strip()
          # split into a list
          date_time = dt.split(' ')
          # strip each component and get rid of blanks
          actual = [component.strip() for component in date_time if len(component.strip()) > 0]
          # date and time should be the only components of the remaining list
          return f'{actual[0]}T{actual[1]}'
      # Every other result just translates directly
      else: return value
  # if jsonify is False, then strings and numbers translate directly.  Time, date, and datetime need
  # to be parsed into the appropriate type
  if sdml_type == SDML_DATE: return datetime.datetime.strptime(value, '%Y-%m-%d').date()
  if sdml_type == SDML_DATETIME: return datetime.datetime.strptime(value, '%y-%m-%d %H:%M:%S')
  if sdml_type == SDML_TIME_OF_DAY: return datetime.datetimestrptime(value, '%H:%M:%S').time()
  return value


def row_from_sql(row, sdml_types, jsonify):
    '''
    Apply translate_value_from_sql to each element of row, using the appropriate sdml type, returning the result
    Arguments:
        - row: a row of values to be translated
        - sdml_types: a list of types, same length as row, sdml_types[i] is the type of row[i]
        - jsonify: if true, return a result that can be jsonified easily
    Returns:
        a list of transformed values
    '''

    return [translate_value_from_sql(row[i], sdml_types[i], jsonify) for i in range(len(sdml_types))]

def rows_from_sql(rows, sdml_types, jsonify):
    '''
    Apply row_from_sql to each element of rows, using the  sdml type list, returning the result as a list of rows
    Arguments:
        - rows: a list of rows of values to be translated
        - sdml_types: a list of types, same length as each row in rows, sdml_types[i] is the type of row[i] for each row in rows
        - jsonify: if true, return a result that can be jsonified easily
    Returns:
        a list of lists transformed values
    '''
    return [row_from_sql(row, sdml_types, jsonify) for row in rows]

class SDMLSqliteTable(SDMLTable):
    '''
    An SDML Table that mirrors an underlying SQLLite Table.  This is in beta, and may move to the sdtp package when it is 
    more mature.  However, SQL is database-engine specific, so this code is left in as an example of how to convert from
    SDQL queries to SQL queries.
    An SDMLSqliteTable uses a SQLite connection to execute queries.  Its function is to issue SQL queries corresponding to the 
    SDQL queries and translate the results back to SDML.
    Most of the function of an SDMLSQLite table is translating values from SDML to SQL and back again, using the utilities translate_value_to_sql
    and row_from_sql and rows_from_sql
    Properties:
      -- schema: the schema of the table
      -- connection: a SQLiteConnection which issues the queries and returns the results
      -- db_table: the name of the table to query
    '''
    def __init__(self, schema, connection, db_table):
        super(SDMLSqliteTable, self).__init__(schema)
        self.connection = connection
        self.db_table = db_table


    def all_values(self, column, jsonify = False):
        '''
        Execute an all_values query, returning the result as a list of SDML values
        Arguments:
          - column: name of the column to get the values for
          - jsonify: return a form that can be converted to json if True
        '''
        sdml_type = self.get_column_type(column)
        sql_result = self.connection.execute_query_return_list(f'Select DISTINCT {column} from {self.db_table}  ORDER BY {column};')
        # The SQL result will be a list of tuples; only the first tuple contains the information we want
        result = [item[0] for item in sql_result]
        # Translate the result into an SDML list
        return [translate_value_from_sql(value, sdml_type, jsonify) for value in result]
       
    def get_column(self, column, jsonify = False):
        '''
        Execute a get_column query, returning the result as a list of SDML values
        Arguments:
          - column: name of the column to get
          - jsonify: return a form that can be converted to json if True
        '''
        sdml_type = self.get_column_type(column)
        result = self.connection.execute_query_return_list(f'Select  {column} from {self.db_table};')
        return [translate_value_from_sql(value, sdml_type, jsonify) for value in result]
    
    def range_spec(self, column, jsonify = False):
        '''
        Execute a range_spec query, returning the result as a list of SDML values
        Arguments:
          - column: name of the column to get the range_spec for
          - jsonify: return a form that can be converted to json if True
        '''
        sdml_type = self.get_column_type(column)
        result = self.connection.execute_query_return_list(f'Select min({column}), max({column}) from {self.db_table};', return_one = True) 
        return [translate_value_from_sql(value, sdml_type, jsonify) for value in result]
    
    # The remainder of this class is a set of methods to generate the WHERE clause in the SQL Select statement for get_filtered_rows.
    # The basic idea is that each SDQL Filter generates a specific expresson in a WHERE clause.  
    # the translate_value_to_sql method is used to translate wire formats

    # Note that the SDQL filter is assumed to be well-formed, over the right columns, etc.

    def _translate_in_list(self, sdql_filter):
        # translate an IN_LIST SDQL Filter (see sdtp_filter.py)
        # into (<col> = u1 OR col = u2 OR ...)
        # where u_i is the SQL version of v_i for the type of this column
        conditions = [f'({sdql_filter.column_name} = {translate_value_to_sql(value, sdql_filter.column_type)})' for value in sdql_filter.value_list]
        return f'({" OR ".join(conditions)})' if len(conditions) > 0 else ''

    def _translate_in_range(self, sdql_filter):
        # translate an IN_RANGE SDQL Filter (see sdtp_filter.py)
        # into (<col> <= <smax> AND <col> >= <smin>)
        # where smax, smin are the SQL values for max, min
        return f'{sdql_filter.column_name} >= {translate_value_to_sql(sdql_filter.min_val, sdql_filter.column_type)} AND {sdql_filter.column_name} <= {translate_value_to_sql(sdql_filter.max_val, sdql_filter.column_type)}'

    def _translate_regex(self, sdql_filter):
        # translate a REGEX_MATCH SDQL Filter (see sdtp_filter.py)
        # into <column_name> REGEXP <expression>.  Since <expression> is a 
        # string, the SQL and SDQL forms are identical
        return f"{sdql_filter.column_name} REGEXP '{sdql_filter.expression}'"

    def _translate_compound(self, operator, arguments):
        # translate a compound operator op (AND or OR) into (a1 <op> a2 <op)...)
        # where a_i is a translation of argument i
        expressions = [f'({self.translate_to_sql(arg)})' for arg in arguments]
        return f' {operator} '.join(expressions)

    def _translate_all(self, sdql_filter):
        # translate  all into an AND compound
        return self._translate_compound('AND', sdql_filter.arguments)

    def _translate_any(self, sdql_filter):
        # translate any into an AND compound
        return self._translate_compound('OR', sdql_filter.arguments)

    def _translate_none(self, sdql_filter):
        # NONE is not or
        return f'NOT{self._translate_any(sdql_filter.arguments)}'

    def translate_to_sql(self, sdql_filter):
        '''
        Get the SQL Where clause for an SDQLFilter (see sdtp_filter.py)
        Arguments:
          - sdql_filter: an SDQL filter
        Returns:
          a SQL WHERE clause (missing WHERE) which expresses the conditions in the SDQL filter
        '''
        methods = {
            'IN_LIST': self._translate_in_list,
            'IN_RANGE': self._translate_in_range,
            'REGEX_MATCH': self._translate_regex,
            'ALL': self._translate_all,
            'ANY': self._translate_any,
            'NONE': self._translate_none
        }
        return methods[sdql_filter.operator](sdql_filter)
    
    
    def get_filtered_rows_from_filter(self, filter=None, columns=[], jsonify = False):
        '''
        Execute the get_filered_rows query, returning the result as a list of lists
        Arguments:
          - filter_spec: Specification of the filter, as a dictionary
          - columns: the names of the columns to return.  Returns all columns if absent
          - jsonify: if True, returns a JSON list.  Default False
        Returns:
          The subset of self.get_rows() which pass the filter as a JSON list if jsonify is True or as a list if jsonify is False
        '''
        # Build the where clause for the SDQL filter conditions, if the SDQL filter is present
        filter_string = self.translate_to_sql(filter) if filter is not None else ''
        where_clause = f'where {filter_string}'  if len(filter_string.strip()) > 0  else ''
        # if there are columns, select the column names, otherwise all columns
        columns_clause = ','.join(columns) if columns is not None and len(columns) > 0 else '*'
        # Form the sql query and execute it
        rows = self.connection.execute_query_return_list(f'SELECT {columns_clause} from {self.db_table} {where_clause};')
        # get the SDML types for the selected columns
        all_types = self.column_types()
        if columns is None or columns == []:
            column_types = all_types
        else:
            names = self.column_names()
            column_indices = [i for i in range(len(names)) if names[i] in columns]
            column_types = [all_types[i] for i in column_indices]
        # Take the returned rows and translate them from SQL according to the column types required
        return rows_from_sql(rows, column_types, jsonify)

# schema = []
# tables = {
#     'presidential_vote':  [{"name": "Year", "type": "number"}, {"name": "State", "type": "string"}, {"name": "Name", "type": "string"}, {"name": "Party", "type": "string"}, {"name": "Votes", "type": "number"}, {"name": "Percentage", "type": "number"}],
#     'presidential_vote_history': [{"name": "State", "type": "string"}, {"name": "Year", "type": "number"}, {"name": "Democratic", "type": "number"}, {"name": "Republican", "type": "number"}, {"name": "Progressive", "type": "number"}, {"name": "Socialist", "type": "number"}, {"name": "Reform", "type": "number"}, {"name": "Other", "type": "number"}],
#     'presidential_margins':  [{"name": "State", "type": "string"}, {"name": "Year", "type": "number"}, {"name": "Margin", "type": "number"}],
#     "nightingale": [
#       {"name": "Month_number", "type": "number"},
#       {"name": "Date", "type": "date"},
#       {"name": "Month", "type": "string"},
#       {"name": "Year", "type": "number"},
#       {"name": "Army", "type": "number"},
#       {"name": "Disease", "type": "number"},
#       {"name": "Wounds", "type": "number"},
#       {"name": "Other", "type": "number"},
#       {"name": "Disease_rate", "type": "number"},
#       {"name": "Wounds_rate", "type": "number"},
#       {"name": "Other_rate", "type": "number"}
#     ],
#     "nationwide_vote": [
#       {
#         "name": "Year",
#         "type": "number"
#       },
#       {
#         "name": "Party",
#         "type": "string"
#       },
#       {
#         "name": "Percentage",
#         "type": "number"
#       }
#     ], 
#     "electoral_college": [
#       {
#         "name": "Year",
#         "type": "number"
#       },
#       {
#         "name": "Democratic",
#         "type": "number"
#       },
#       {
#         "name": "Republican",
#         "type": "number"
#       },
#       {
#         "name": "Other",
#         "type": "number"
#       }
#     ]
# }
# sqlite_tables = {}
# connection = SQLiteConnection('presidential_vote.db')
# for (name, schema) in tables.items():
#     sqlite_tables[name] = SDMLSqliteTable(schema, connection, name)

# pass