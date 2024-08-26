"""Simple Table Examples for the Simple Data Transfer Protocol."""

# BSD 3-Clause License

# Copyright (c) 2024, The Regents of the University of California (Regents)
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import sys
import os
from glob import glob
from json import load
import datetime

'''
This is a simple SDTP Server, designed primarily for illustrative purposes -- this server is configured
by the two variables SDTP_PATH and TABLE_FACTORIES in conf.py.  See the documentation in sample_conf.py.
This is a very thin overlay on the server in sdtp_server.py, with a /, /help method which describes the available routes and required variables.

'''


from sdtp import sdtp_server_blueprint, SDMLTable,  jsonifiable_column, jsonifiable_rows
from sdtp import  SDML_NUMBER, SDML_BOOLEAN, SDML_DATE, SDML_DATETIME, SDML_TIME_OF_DAY, SDML_STRING
from flask import Flask
import sqlite3
import re
from sqlite_interface import SDMLSqliteTable, SQLiteConnection


# schema = []
tables = {
    'presidential_vote':  [{"name": "Year", "type": "number"}, {"name": "State", "type": "string"}, {"name": "Name", "type": "string"}, {"name": "Party", "type": "string"}, {"name": "Votes", "type": "number"}, {"name": "Percentage", "type": "number"}],
    'presidential_vote_history': [{"name": "State", "type": "string"}, {"name": "Year", "type": "number"}, {"name": "Democratic", "type": "number"}, {"name": "Republican", "type": "number"}, {"name": "Progressive", "type": "number"}, {"name": "Socialist", "type": "number"}, {"name": "Reform", "type": "number"}, {"name": "Other", "type": "number"}],
    'presidential_margins':  [{"name": "State", "type": "string"}, {"name": "Year", "type": "number"}, {"name": "Margin", "type": "number"}],
    "nightingale": [
      {"name": "Month_number", "type": "number"},
      {"name": "Date", "type": "date"},
      {"name": "Month", "type": "string"},
      {"name": "Year", "type": "number"},
      {"name": "Army", "type": "number"},
      {"name": "Disease", "type": "number"},
      {"name": "Wounds", "type": "number"},
      {"name": "Other", "type": "number"},
      {"name": "Disease_rate", "type": "number"},
      {"name": "Wounds_rate", "type": "number"},
      {"name": "Other_rate", "type": "number"}
    ],
    "nationwide_vote": [
      {
        "name": "Year",
        "type": "number"
      },
      {
        "name": "Party",
        "type": "string"
      },
      {
        "name": "Percentage",
        "type": "number"
      }
    ], 
    "electoral_college": [
      {
        "name": "Year",
        "type": "number"
      },
      {
        "name": "Democratic",
        "type": "number"
      },
      {
        "name": "Republican",
        "type": "number"
      },
      {
        "name": "Other",
        "type": "number"
      }
    ]
}

connection = SQLiteConnection('presidential_vote.db')
for (name, schema) in tables.items():
    table = SDMLSqliteTable(schema, connection, name)
    sdtp_server_blueprint.table_server.add_sdtp_table({'name': name, 'table': table})

app = Flask(__name__)

app.register_blueprint(sdtp_server_blueprint)


additional_routes = [
     {"url": "/, /help", "headers": "", "method": "GET", "description": "print this message"},
     {"url": "/cwd", "headers": "", "method": "GET", "description": "Show the working directory on the server"},
]

@app.route('/help', methods=['POST', 'GET'])
@app.route('/', methods=['POST', 'GET'])
def show_routes():
    '''
    Show the API for the table server
    Arguments: None
    '''
    pages = sdtp_server_blueprint.ROUTES + additional_routes
    page_strings = [f'<li>{page}</li>' for page in pages]

    return f'<body  style="font-family: Arial, Helvetica, Sans-Serif;"><h1>Supported Methods</h1><ul>{"".join(page_strings)}</ul></body>'



@app.route('/cwd')
def cwd():
    return os.getcwd()


if __name__ == '__main__':
    app.run()