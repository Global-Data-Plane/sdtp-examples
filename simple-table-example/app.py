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

'''
This is a simple SDTP Server, designed primarily for illustrative purposes -- this server is configured
by the two variables SDTP_PATH and TABLE_FACTORIES in conf.py.  See the documentation in sample_conf.py.
This is a very thin overlay on the server in sdtp_server.py, with a /, /help method which describes the available routes and required variables.

'''

from conf import SDTP_PATH

from sdtp import sdtp_server_blueprint
from flask import Flask
from flask_cors import CORS
from pathlib import Path


app = Flask(__name__)
# turn on CORS
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

app.register_blueprint(sdtp_server_blueprint)


#
# Load a table.  filename is a valid path and an SDML file.
# 

def _load_table(filename):
    # filename: path to an SDML file
    # The filename is <path>/table_name.sdml, stores this in table_name
    with open(filename, 'r') as fp:
        table_dictionary = load(fp)
        sdtp_server_blueprint.table_server.add_sdtp_table_from_dictionary(Path(filename).stem, table_dictionary)

# 
# Load all the tables on SDTP_PATH.  
#

if SDTP_PATH is not None and len(SDTP_PATH) > 0:
    for path in SDTP_PATH:
        if os.path.exists(path) and os.path.isdir(path):
            files = glob(f'{path}/*.sdml')
            for filename in files:
                _load_table(filename)


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