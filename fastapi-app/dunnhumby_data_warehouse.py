from sqlalchemy.orm import Session
import models
import pprint
from database import engine, get_db
import datetime as dt
#from sqlalchemy import insert, delete, update
from my_url import _SQLALCHEMY_DATABASE_URL
#from fastapi import Depends

from sqlalchemy import inspect

import datetime as dt
import pandas as pd
import numpy as np


# a wrapper to instantiate a session allows us to ensure the database connection is closed after our transaction; that a new Session is generated each time we interact with the db.
# Dependency


class DunnHumbyDataWarehouse:
    """
    DataLake reads from defined data sources in ../data/ (in this case .csv files) and provides a level of control over that process:
        - idempotency; 
            - compare row indexes from your data source to the row indexes in your final database
        - availability;
            - perform batch/cron jobs to either load data into db

        - incorporate logging tools of your choice, here we use a basic .setter to record and print the progress   
        
        """

    def __init__(self,
                 data_folder:str="data/",
                 db:Session = get_db()):
        
        self.db=db
        self.data_folder = data_folder

        ### instantiate logging...
        self._log = ""

        ### specific data sources/endpoints using your prefix; source URL (or disk data)
        self.table_names = ['campaign_desc',
                            'campaign_table',
                            'causal_data',
                            'coupon',
                            'coupon_redempt',
                            'hh_demographic',
                            'product',
                            'transaction_data',

                            'hh_summary',
                            'daily_campaign_sales',
                            ]

        ### along with a map of your table models (the abstraction layer of SQLALchemy)
        self.table_models = [models.CampaignDesc,
                            models.CampaignTable,
                            models.CausalData,
                            models.Coupon,
                            models.CouponRedempt,
                            models.HHDemographic,
                            models.Product,
                            models.TransactionData
                            ]

        ### map the two together for reference
        self.name_model_map = dict(zip(self.table_names, self.table_models)) 

        # hardcoded here for simplicity; 
        # THESE VALUES UPDATE EVERY TIME YOU RUN `self.update_table()`/`self.update_many()`  ~~
        self.datasource_rowcounts = {'campaign_desc': 30,
                                    'campaign_table': 7208,
                                    'causal_data': 36786524,
                                    'coupon': 124548,
                                    'coupon_redempt': 2318,
                                    'hh_demographic': 801,
                                    'product': 92353,
                                    'transaction_data': 2595732,
                                    
                                    # gold tables
                                    'hh_summary' : 801, 
                                    'daily_campaign_sales' : 17597,} 
        
        # live updating rowcounts from the data lake (post-ingestion)
        self.database_rowcounts = dict()
        ### ping db to find existing rowcount/index for known tables
        self.update_database_rowcounts()

        # check the rowcounts for all tables versus previously known indexes from datasource
        #table_names = inspect(engine).get_table_names()


        # hardcoded table names
        for existing_table in self.table_names:
            try:
                assert self.datasource_rowcounts[existing_table] == self.update_database_rowcount(existing_table), f"error with table {existing_table}"
                self.log = f"table {existing_table} is up to date"
        
            except BaseException as e:
                self.log = f"rowcount indexes for {existing_table} don't match"
                self.log = f"{e}"
                continue

        #pprint.pprint(self.database_rowcounts)
        # output most recent log?
        # with open(f'logs/{dt.datetime.now.utc()[:10]}') as f:
        #     f.writelines(self.log)
        

### UTILITY FUNCTIONS
    def clean_query(self, query):
        return " ".join(query.replace('\n', ' ').replace('\t', ' ').split())
                        
    def query_db(self, query):
        conn = engine.raw_connection()
        cur = conn.cursor()
        cur.execute(self.clean_query(query))
        res = cur.fetchall()
        return res

    # def return_table(self, query):
    #     conn = engine.raw_connection()
    #     cur = conn.cursor()
    #     cur.execute(self.clean_query(query))
    #     colnames = [x[0] for x in cur.description]
    #     res = cur.fetchall()
    #     return pd.DataFrame(res, columns=colnames)

    def get_table(self, table_name:str):
        try:
            con = engine.raw_connection()
            cursor = con.cursor()
            cursor.execute(f'select * from {table_name}')
            colnames = [x[0] for x in cursor.description]
            res = cursor.fetchall()
            return pd.DataFrame(res, columns=colnames)

        except BaseException as e:
            self.log = f"{str(e)} error in get_existing_rowcount"
            return e
    
    def update_database_rowcount(self, table_name:str):
        '''call the database to get the count() of rows 
        return the existing index/rowcount from the database
        '''
        try:
            con = engine.raw_connection()
            cursor = con.cursor()
            cursor.execute(f'select count(1) from {table_name}')
            res = cursor.fetchall()
        except BaseException as e:
            self.log = f"{str(e)} error in get_existing_rowcount"
            return e
        
        self.database_rowcounts[table_name] = res[0][0]
        return res[0][0]
    
    @property
    def database_tables(self):
        return inspect(engine).get_table_names()


    def update_database_rowcounts(self):
        '''calls self.get_existing_rowcounts() on each self.table_name'''
        for x in self.database_tables:
            self.update_database_rowcount(x)


    def delete_known_table(self, table_name:str):
        '''drop a table from the database'''
        con = engine.raw_connection()
        cursor = con.cursor()
        cursor.execute(f'drop table {table_name}')
    

    def delete_known_tables(self):
        '''drop all tables in the database'''
        for x in self.table_names:
            self.delete_known_table(x)

            
    def update_table(self, table_name:str, db:Session=next(get_db())):
        '''this function could be adapted to conditionally update a table instead of re-writing it/loading it once
        
        this function isn't optimized well because of lack of clarity of the use case...
        
        needs to be refactored already in the if loop'''


        # check the new data source index/rowcount (here by loading the data...not optimal)
        filename = self.data_folder+table_name+'.csv'

        # using pandas
        df = pd.read_csv(filename)

        # compare indices. Only update/add rows from the end of existing data through to your standardized migration datetime.
        datasource_rowcount = self.datasource_rowcounts[table_name] = df.shape[0] 
        database_rowcount = self.update_database_rowcount(table_name)
        self.log = f"***** Updating data lake table: {table_name} from raw data source*****"
        self.log = f"data source has {datasource_rowcount} rows, data lake has {database_rowcount}"

        start_load_index = 0

        if datasource_rowcount == database_rowcount:
            # data source index matches data lake index/rowcount
            self.log = f"   table {table_name} is fully updated"
            # return early if no update required
            return None
        
        if (database_rowcount != start_load_index) and (database_rowcount != datasource_rowcount):
            # if there is inconsistency, the procedure here is to simply delete table and start over... also not optimal
            self.log = f"   deleting rows from data lake table: {table_name}"
            try:
                self.delete_known_table(table_name)
            except BaseException as e:
                self.log = f" error {e} with {table_name}"

        
        # if not return early, write data (this should include a non-naive index-based insertion approach; or an update call instead of a pd.to_sql...)
        self.log = f"   loading raw data from source: {table_name} to Data Lake"   
        
        # write data using pandas (for now)
        df.to_sql(name=table_name,
                   con=_SQLALCHEMY_DATABASE_URL,
                   if_exists='append',
                #    if_exists='replace',
                   chunksize=999,
                   method='multi')

        self.update_database_rowcount(table_name)
        self.log = f"Data Lake table {table_name}  has {self.database_rowcounts[table_name]} rows, of {self.datasource_rowcounts[table_name]} in source."
        self.log = f"***************************************"


    def update_many(self,
                     all_names:list=None,
                     db:Session=next(get_db())):
        '''function to insert all data from the known tables in self.table_names
        pass a list of table names if not updating all tables'''

        if all_names == None:
            all_names = self.table_names

        for name in all_names:
            self.update_table(table_name=name, db=db)

        self.log = f"Tables {all_names} have been updated in the data lake."
        self.log = f"***************************************"

    ### logger
    @property
    def log(self):
        return self._log
    
    @log.setter
    def log(self, new:str):
        print(new, flush=True)
        self._log += f"\n {dt.datetime.utcnow()}" + new

    @log.deleter
    def log(self):
        try:
            with open(f'{dt.datetime.now()}_log.txt', 'w') as f:
                f.writelines(self._log)
        finally:
            pass

    def print_log(self):
        pprint.pprint(self.log)


if __name__ == '__main__':

    a = DunnHumbyDataWarehouse()

    a.update_many()
    # # pprint.pprint(a.log)







