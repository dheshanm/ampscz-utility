#!/usr/bin/env python

import pandas as pd
import json
import numpy as np
from os import getcwd, chdir, makedirs
from os.path import dirname, basename, abspath
from datetime import datetime, timedelta
import sys
from glob import glob


# Shift REDCap dates by one of [-14,-7,7,14] randomly chosen days
# Usage:
# __file__ NDA_ROOT /path/to/redcap_data_dict.csv "Pronet/PHOENIX/PROTECTED/*/raw/*/surveys/*.Pronet.json"
# __file__ PHOENIX_PROTECTED /path/to/redcap_data_dict.csv "*/raw/*/surveys/*.Pronet.json"

_shift= [-14,-7,7,14]
L= len(_shift)
prob= [1/L]*L

df=pd.read_csv(sys.argv[2], encoding='ISO-8859-1')

dir_bak=getcwd()
chdir(sys.argv[1])

files=glob(sys.argv[3])
dfshift=pd.read_csv('date_offset.csv')
dfshift.set_index('subject',inplace=True)
save=0
for file in files:
    subject=basename(file).split('.')[0]

    if subject not in dfshift.index:
        # randomize according to multinomial distribution
        shift= _shift[np.where(np.random.multinomial(1,prob))[0][0]]
        dfshift.at[subject,'days']=shift
        save=1

if save:
    dfshift.to_csv('date_offset.csv')


# when downloaded through GUI
var_header='Variable / Field Name'
field_type='Field Type'
form_header='Form Name'
branch_header='Branching Logic (Show field only if...)'
calc_header='Choices, Calculations, OR Slider Labels'
valid_header='Text Validation Type OR Show Slider Number'

# when downloaded through API
if var_header not in df:
    var_header='field_name'
    field_type='field_type'
    form_header='form_name'
    branch_header='branching_logic'
    calc_header='select_choices_or_calculations'
    valid_header='text_validation_type_or_show_slider_number'

df.set_index(var_header,inplace=True)


for file in files:

    # skip unchanged JSONs

    # load json
    with open(file) as f:
        dict1=json.load(f)
    
    subject=basename(file).split('.')[0]
    shift= int(dfshift.loc[subject,'days'])
    
    print('Processing', file)

    for d in dict1:
        for name,value in d.items():
            try:
                df.loc[name]
            except:
                continue

            if df.loc[name,valid_header]=='date_ymd':
                if value and value not in ['-3','-9','1909-09-09','1903-03-03','1901-01-01']:
                    _format='%Y-%m-%d'
                    # shift it
                    value=datetime.strptime(value,_format)+timedelta(days=shift)
                    d[name]=value.strftime(_format)

            elif df.loc[name,valid_header]=='datetime_ymd':
                if value:
                    _format='%Y-%m-%d %H:%M'
                    # shift it
                    value=datetime.strptime(value,_format)+timedelta(days=shift)
                    d[name]=value.strftime(_format)

    
    file=abspath(file)
    file=file.replace('PROTECTED/','GENERAL/')
    file=file.replace('/raw/','/processed/')

    makedirs(dirname(file), mode=0o775, exist_ok=True)
    with open(file,'w') as f:
        json.dump(dict1,f)


chdir(dir_bak)


