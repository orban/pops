#!/usr/bin/env python

# adopted from pandas_dbms.py
# @ https://gist.github.com/catawbasam/3164289
import os, sys, time, re, json, pdb, datetime
import numpy as np
import pandas as pd
import pandas.io.sql as psql
from dateutil import parser
import psycopg2

dbtypes={
    'mysql' : {'DATE':'DATE', 'DATETIME':'DATETIME',           'INT':'BIGINT',  'FLOAT':'FLOAT',  'VARCHAR':'VARCHAR'},
    'oracle': {'DATE':'DATE', 'DATETIME':'DATE',               'INT':'NUMBER',  'FLOAT':'NUMBER', 'VARCHAR':'VARCHAR2'},
    'sqlite': {'DATE':'TIMESTAMP', 'DATETIME':'TIMESTAMP',     'INT':'NUMBER',  'FLOAT':'NUMBER', 'VARCHAR':'VARCHAR2'},
    'postgresql': {'DATE':'TIMESTAMP', 'DATETIME':'TIMESTAMP', 'INT':'BIGINT',  'FLOAT':'REAL',   'VARCHAR':'TEXT'},
}

def nan2none(df):
    dnp = df.values
    for rw in dnp:
        rw2 = tuple([ None if v==np.Nan else v for v in rw])
        
    tpl_list= [ tuple([ None if v==np.Nan else v for v in rw]) for rw in dnp ] 
    return tpl_list
    
def db_colname(pandas_colname):
    '''convert pandas column name to a DBMS column name
        TODO: deal with name length restrictions, esp for Oracle
    '''
    colname =  pandas_colname.replace(' ','_').strip()                  
    return colname

def postgresql_copy_from(df, name, con):
    # append data into existing postgresql table using COPY
    
    # 1. convert df to csv no header
    # deal with datetime64 to_csv() bug
    have_datetime64 = False
    dtypes = df.dtypes
    for i, k in enumerate(dtypes.index):
        dt = dtypes[k]
        print 'dtype', dt, dt.itemsize
        if str(dt.type)=="<type 'numpy.datetime64'>":
            have_datetime64 = True

    if have_datetime64:
        d2=df.copy()    
        for i, k in enumerate(dtypes.index):
            dt = dtypes[k]
            if str(dt.type)=="<type 'numpy.datetime64'>":
                d2[k] = [ v.to_pydatetime() for v in d2[k] ]                
        #convert datetime64 to datetime
        #ddt= [v.to_pydatetime() for v in dd] #convert datetime64 to datetime
        d2.to_csv('output', sep='\t', header=False, index=False)
    else:
        df.to_csv('output', sep='\t', header=False, index=False)                        
    
    # 2. copy from
    with open('output') as f:
        cur = con.cursor()
        cur.copy_from(f, name)    
        con.commit()
    try: 
        os.system('rm output')
    except:
        pass
    return

#source: http://www.gingerandjohn.com/archives/2004/02/26/cx_oracle-executemany-example/
def convertSequenceToDict(list):
    """for  cx_Oracle:
        For each element in the sequence, creates a dictionary item equal
        to the element and keyed by the position of the item in the list.
        >>> convertListToDict(("Matt", 1))
        {'1': 'Matt', '2': 1}
    """
    dict = {}
    argList = range(1,len(list)+1)
    for k,v in zip(argList, list):
        dict[str(k)] = v
    return dict

def get_schema(frame, name, flavor):
    types = dbtypes[flavor]  #deal with datatype differences
    column_types = []
    dtypes = frame.dtypes
    for i,k in enumerate(dtypes.index):
        dt = dtypes[k]
        #print 'dtype', dt, dt.itemsize
        if str(dt.type)=="<type 'numpy.datetime64'>":
            sqltype = types['DATETIME']
        elif issubclass(dt.type, np.datetime64):
            sqltype = types['DATETIME']
        elif issubclass(dt.type, (np.integer, np.bool_)):
            sqltype = types['INT']
        elif issubclass(dt.type, np.floating):
            sqltype = types['FLOAT']
        else:
            sampl = frame[ frame.columns[i] ][0]
            #print 'other', type(sampl)    
            if str(type(sampl))=="<type 'datetime.datetime'>":
                sqltype = types['DATETIME']
            elif str(type(sampl))=="<type 'datetime.date'>":
                sqltype = types['DATE']                   
            else:
                if flavor in ('mysql','oracle'):                
                    size = 2 + max( (len(str(a)) for a in frame[k]) )
                    print k,'varchar sz', size
                    sqltype = types['VARCHAR'] + '(?)'.replace('?', str(size) )
                else:
                    sqltype = types['VARCHAR']
        colname =  db_colname(k)  #k.upper().replace(' ','_')                  
        column_types.append((colname, sqltype))
    columns = ',\n  '.join('%s %s' % x for x in column_types)
    template_create = """CREATE TABLE %(name)s (
                      %(columns)s
                    );"""    
    #print 'COLUMNS:\n', columns
    create = template_create % {'name' : name, 'columns' : columns}
    return create
    
def write_frame(frame,name,cnx):
    cnx.reset()
    cur = cnx.cursor()
    cnx_exe = cur.execute
    cnx_exe('DROP TABLE if EXISTS %s;' %name)
    
    # create table
    schema = get_schema(frame, name, 'postgresql')
    cnx_exe(schema)
    
    # copy into postgresql
    postgresql_copy_from(frame, name, cnx)
    cnx.commit()
    return None

###############################################################################
if __name__=='__main__':
    # ------------------------------------------
    # connecting to a PostgreSQL database
    # ------------------------------------------
    cnx = psycopg2.connect(host='localhost', database='popsfundamental', 
                               user='jhuang')
    cur = cnx.cursor()
    cnx_exe = cur.execute
    print psql.read_frame("SELECT VERSION()",cnx)
    cnx_exe("""
    DROP TABLE if EXISTS abc;
    CREATE TABLE abc AS
    SELECT VERSION();
    """)
    cnx.commit()
    cnx.reset()

    test_data = {
        "name": [ 'Joe', 'Bob', 'Jim', 'Suzy', 'Cathy', 'Sarah' ],
        "hire_date": [ datetime.date(2012,1,1), datetime.date(2012,2,1), datetime.date(2012,3,1), datetime.date(2012,4,1), datetime.date(2012,5,1), datetime.date(2012,6,1) ],
        "erank": [ 1,   2,   3,   4,   5,   6  ],
        "score": [ 1.1, 2.2, 3.1, 2.5, 3.6, 1.8]
    }
    df = pd.DataFrame(test_data)
    print '-'*20
    print 'The data frame created is'
    print df
    print '-'*20
    name='test_df'
    
    # put the table into PostSQL
    pdb.set_trace()
    print 'writing frame...'
    write_frame(df, name, cnx)
    print 'done writing'
    _df = psql.read_frame('SELECT * FROM %s;' %name, cnx)
    print '-'*20
    print 'The data frame return is'
    print _df
    print '-'*20
    # delete the table from PostSQL
    cnx_exe('DROP TABLE if EXISTS %s;' %name)

