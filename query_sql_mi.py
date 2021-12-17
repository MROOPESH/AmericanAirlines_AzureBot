
from io import BytesIO
import pandas as pd
import json
import pyarrow
import pyarrow.parquet as pq

import io
import sys
from azure.identity import ClientSecretCredential
from azure.identity import DeviceCodeCredential 
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from datetime import date
import datetime
import pyodbc

class QuerySQLMI:
    
    def init(self):
        tenant_id = "49793faf-eb3f-4d99-a0cf-aef7cce79dc1" # Org Tenant ID
        client_id = "eb3d741f-cf2d-47a1-ba40-50e4888ba29d" # Azure Bot Microsoft App Id
        client_secret = "Bbc7Q~DhshhnU7S_xeVQ~rYkKI5.2xtsJylnw" # Azure Bot Client Secret Value. (masked)
        client_id_storage = "5add4ee6-db8d-491f-8f63-50bec19a3c6e" #Application ID for SP of storage account.

        secret_name = 'ba-p-group050-orionsp-secret' # KeyVault entry for Azure BOT 
        secret_name_mi = "ba-p-group050-sp-secret-sqlmi"
        vault_uri = 'https://ba-p-zeaus-group050-kv.vault.azure.net/'
        authority_host_uri = "login.microsoftonline.com"
        keyvault_resource_uri = 'https://vault.azure.net'

        #Orion Datalake 
        storage_account_name=  'aabaoriondlsprod'
        file_system_name = 'pplcorepkg'
        directory_path = "prod/delta-pkg/workforce_jobinfo_master/"

        def get_kvvalue(name):
            credential = ClientSecretCredential(tenant_id, client_id, client_secret)
            client = SecretClient(vault_uri, credential)
            try:
                secret_bundle = client.get_secret(name)
                return secret_bundle.value
            except:
                print(sys.exc_info())
            return '' 
        # we create the connection variable cnxn, cnxn_hiring to connect to database and query tables...
        
        global driver, server, database, database_hiring, username, password
        server = 'ba-p-zeaus-group050-sqlmi-bot.public.5791aec5f884.database.windows.net,3342'
        database = 'pplcorepkg_db'
        database_hiring = "talentpkg_db"
        username = 'botadmin'  
        password = '{'+get_kvvalue(secret_name_mi)+'}' 
        driver= '{ODBC Driver 17 for SQL Server}'
        global hrdata_table, hiringdata_table, hiringappl_table
        hrdata_table = "jobinfo_master"
        hiringdata_table = "requisition_master"
        hiringappl_table = "appl_master"
        #cnxn = pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=3342;DATABASE='+database+';UID='+username+';PWD='+ password)
        #cnxn_hiring = pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=3342;DATABASE='+database_hiring+';UID='+username+';PWD='+ password)

    def hrdata_cnxn(self):
        cnxn = pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=3342;DATABASE='+database+';UID='+username+';PWD='+ password)        
        return cnxn

    def hiringdata_cnxn(self):        
        cnxn_hiring = pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=3342;DATABASE='+database_hiring+';UID='+username+';PWD='+ password)
        return cnxn_hiring

    # validate_empid is a mehtod to valdiate the Employee/Personal id entered by the user in text box of adaptive card
    def validate_empid(self, emp_id: int): 
        print("validate_empid")  
        data = pd.read_sql_query(f"SELECT * FROM " + hrdata_table + " where prsnel_id in ('" + str(emp_id) + "')", self.hrdata_cnxn())
        print(data.shape[0]!=0)
        return data.shape[0]!=0

    # This method is to fetch employee details for Searc Emp details by Employee ID...
    def fetch_emp_details_by_empid(self, emp_id: int):  
        print("fetch_emp_details_by_empid") 
        df = pd.read_sql_query(f"SELECT * FROM " + hrdata_table + " where prsnel_id in ('" + str(emp_id) + "')", self.hrdata_cnxn())
        df['event_start_dt'] = pd.to_datetime(df['event_start_dt']).dt.date        
        df["prsnel_id"] = df["prsnel_id"].astype('int')
        df["job_tos_is1"] = df["job_tos_is1"].astype('int')
        # we create a dictionary and store the results to return from this method...
        response = {}
        response['emplmt_status_desc'] = df[(df['prsnel_id']==emp_id) & (df['job_tos_is1'] == 1)]['emplmt_status_desc'].values[0]
        response['termination_ind'] = df[(df['prsnel_id']==emp_id) & (df['job_tos_is1'] == 1)]['termination_ind'].values[0]
        response['job_title_desc'] = df[(df['prsnel_id']==emp_id) & (df['job_tos_is1'] == 1)]['job_title_desc'].values[0]
        try:
            response['hire_dt'] = df[(df['prsnel_id'] == emp_id) & (df['event_type_nm'] == 'Hire (H)')]['event_start_dt'].values[0]
        except:
            response['hire_dt'] = "NULL"

        if response['emplmt_status_desc'] != "Terminated":
            response['termination_dt'] = "NULL"
        else:
            response['termination_dt'] = df[(df['prsnel_id'] == emp_id) & (df['event_type_nm'] == 'Termination (26)')]['event_start_dt'].values[0]
        
        response['job_positn_id'] = df[(df['prsnel_id']==emp_id) & (df['job_tos_is1'] == 1)]['job_positn_id'].values[0]
        response['cost_center_cd'] = str(df[(df['prsnel_id']==emp_id) & (df['job_tos_is1'] == 1)]['cost_center_cd'].values[0]) + " - " + df[(df['prsnel_id']==emp_id) & (df['job_tos_is1'] == 1)]['cost_center_desc'].values[0]
        response['department_unit'] = str(df[(df['prsnel_id']==emp_id) & (df['job_tos_is1'] == 1)]['department_unit'].values[0]) + " - " + df[(df['prsnel_id']==emp_id) & (df['job_tos_is1'] == 1)]['department_unit_desc'].values[0]
        response['division_nm'] = df[(df['prsnel_id']==emp_id) & (df['job_tos_is1'] == 1)]['division_nm'].values[0]        
        response['location_cd'] = df[(df['prsnel_id']==emp_id) & (df['job_tos_is1'] == 1)]['location_cd'].values[0]
        response['rptg_wrkgrp'] = df[(df['prsnel_id']==emp_id) & (df['job_tos_is1'] == 1)]['rptg_wrkgrp'].values[0]
        response['mgr_name'] = df[(df['prsnel_id']==emp_id) & (df['job_tos_is1'] == 1)]['mgr_name'].values[0]
        response['md_name'] = df[(df['prsnel_id']==emp_id) & (df['job_tos_is1'] == 1)]['md_name'].values[0]        
        
        return response


    # Insights query related functions
    def insights_non_terminated(self, criteria1):
        # logic for Headcount of Non-terminated employees query...
        if str(criteria1) == 'cost_center_cd': 
            query = "SELECT Top 10 cost_center_cd, cost_center_desc, count(*) as count FROM " + hrdata_table + " where job_tos_is1 in ('1') and emplmt_status_desc not in ('Terminated') group by cost_center_cd, cost_center_desc order by count desc"
            df3 = pd.read_sql_query(query, self.hrdata_cnxn())   
            cols = ['cost_center_cd', 'cost_center_desc']
            # we are merging cost_center_cd and cost_center_desc columns into one column and dropping both of them...
            df3['cost_center'] = df3.apply(lambda r: "{0} ({1})".format(r['cost_center_desc'], r['cost_center_cd']), axis=1)
            df3 = df3.drop(['cost_center_cd', 'cost_center_desc'], 1)

        elif str(criteria1) == 'department_unit':
            query = "SELECT Top 10 department_unit, department_unit_desc, count(*) as count FROM " + hrdata_table + " where job_tos_is1 in ('1') and emplmt_status_desc not in ('Terminated') group by department_unit, department_unit_desc order by count desc"
            df3 = pd.read_sql_query(query, self.hrdata_cnxn())
            cols = ['department_unit', 'department_unit_desc']
            # we are merging department_unit and department_unit_desc columns into one column and dropping both of them...
            df3['department'] = df3.apply(lambda r: "{0} ({1})".format(r['department_unit_desc'], r['department_unit']), axis=1)
            df3 = df3.drop(['department_unit', 'department_unit_desc'], 1)

        else:
            query = f"SELECT Top 10 count(*) as count, " + criteria1 + " FROM " + hrdata_table + " where job_tos_is1 in ('1') and emplmt_status_desc not in ('Terminated') group by " + criteria1 + " order by count desc"
            df3 = pd.read_sql_query(query, self.hrdata_cnxn())

        print(dict(df3.values))
        return dict(df3.values)
        
    def insights_hires_by_hiredate(self, criteria1, from_date, to_date):
        # logic for No.of hires by hire date query...
        # since, to_date is optional to enter in adpative card, there are two cases as follows...
        # to_date is either empty or to_date is a date...
        if to_date == "":
            if str(criteria1) == 'cost_center_cd':
                query = "SELECT Top 10 cost_center_cd, cost_center_desc, count(*) as count FROM " + hrdata_table + " where job_tos_is1 in ('1') and event_type_nm in ('Hire (H)') and event_start_dt >= '" + from_date + "' and event_start_dt <= '" + str(pd.to_datetime(date.today())) + "' group by cost_center_cd, cost_center_desc order by count desc"
                df3 = pd.read_sql_query(query, self.hrdata_cnxn()) 
                cols = ['cost_center_cd', 'cost_center_desc']
                # we create the cost_center column and drop cost_center_cd, cost_center_desc columns
                df3['cost_center'] = df3.apply(lambda r: "{0} ({1})".format(r['cost_center_desc'], r['cost_center_cd']), axis=1)
                df3 = df3.drop(['cost_center_cd', 'cost_center_desc'], 1)

            elif str(criteria1) == 'department_unit':
                query = "SELECT Top 10 department_unit, department_unit_desc, count(*) as count FROM " + hrdata_table + " where job_tos_is1 in ('1') and event_type_nm in ('Hire (H)') and event_start_dt >= '" + from_date + "' and event_start_dt <= '" + str(pd.to_datetime(date.today())) + "' group by department_unit, department_unit_desc order by count desc"
                df3 = pd.read_sql_query(query, self.hrdata_cnxn())
                cols = ['department_unit', 'department_unit_desc']
                # we create the department column and drop department_unit, department_unit_desc columns
                df3['department'] = df3.apply(lambda r: "{0} ({1})".format(r['department_unit_desc'], r['department_unit']), axis=1)
                df3 = df3.drop(['department_unit', 'department_unit_desc'], 1)

            else:
                query = "SELECT Top 10 count(*) as count, " + criteria1 + "  FROM " + hrdata_table + " where job_tos_is1 in ('1') and event_type_nm in ('Hire (H)') and event_start_dt >= '" + from_date + "' and event_start_dt <= '" + str(pd.to_datetime(date.today())) + "' group by (" + criteria1 + ") order by count desc"
                df3 = pd.read_sql_query(query, self.hrdata_cnxn())

        else:    
            if str(criteria1) == 'cost_center_cd':  
                query = "SELECT Top 10 cost_center_cd, cost_center_desc, count(*) as count FROM " + hrdata_table + " where job_tos_is1 in ('1') and event_type_nm in ('Hire (H)') and event_start_dt >= '" + from_date + "' and event_start_dt <= '" + to_date + "' group by cost_center_cd, cost_center_desc order by count desc"
                df3 = pd.read_sql_query(query, self.hrdata_cnxn()) 
                cols = ['cost_center_cd', 'cost_center_desc']
                # we create the cost_center column and drop cost_center_cd, cost_center_desc columns
                df3['cost_center'] = df3.apply(lambda r: "{0} ({1})".format(r['cost_center_desc'], r['cost_center_cd']), axis=1)
                df3 = df3.drop(['cost_center_cd', 'cost_center_desc'], 1)

            elif str(criteria1) == 'department_unit':
                query = "SELECT Top 10 department_unit, department_unit_desc, count(*) as count FROM " + hrdata_table + " where job_tos_is1 in ('1') and event_type_nm in ('Hire (H)') and event_start_dt >= '" + from_date + "' and event_start_dt <= '" + to_date + "' group by department_unit, department_unit_desc order by count desc"
                df3 = pd.read_sql_query(query, self.hrdata_cnxn())
                cols = ['department_unit', 'department_unit_desc']
                # we create the department column and drop department_unit, department_unit_desc columns
                df3['department'] = df3.apply(lambda r: "{0} ({1})".format(r['department_unit_desc'], r['department_unit']), axis=1)
                df3 = df3.drop(['department_unit', 'department_unit_desc'], 1)

            else:
                query = "SELECT Top 10 count(*) as count, " + criteria1 + " FROM " + hrdata_table + " where job_tos_is1 in ('1') and event_type_nm in ('Hire (H)') and event_start_dt >= '" + from_date + "' and event_start_dt <= '" + to_date + "' group by (" + criteria1 + ") order by count desc"
                df3 = pd.read_sql_query(query, self.hrdata_cnxn())

        print(dict(df3.values))
        return dict(df3.values)

    def insights_trmns_by_terminationdate(self, criteria1, from_date, to_date):
        # logic for No.of terminations by termination date query...
        # since, to_date is optional to enter in adpative card, there are two cases as follows...
        # to_date is either empty or to_date is a date...
        if to_date == "":
            if str(criteria1) == 'cost_center_cd':
                query = "SELECT Top 10 cost_center_cd, cost_center_desc, count(*) as count FROM " + hrdata_table + " where job_tos_is1 in ('1') and event_type_nm in ('Termination (26)') and event_start_dt >= '" + from_date + "' and event_start_dt <= '" + str(pd.to_datetime(date.today())) + "' group by cost_center_cd, cost_center_desc order by count desc"
                df3 = pd.read_sql_query(query, self.hrdata_cnxn())     
                cols = ['cost_center_cd', 'cost_center_desc']
                # we create the cost_center column and drop cost_center_cd, cost_center_desc columns
                df3['cost_center'] = df3.apply(lambda r: "{0} ({1})".format(r['cost_center_desc'], r['cost_center_cd']), axis=1)
                df3 = df3.drop(['cost_center_cd', 'cost_center_desc'], 1)

            elif str(criteria1) == 'department_unit':
                query = "SELECT Top 10 department_unit, department_unit_desc, count(*) as count FROM " + hrdata_table + " where job_tos_is1 in ('1') and event_type_nm in ('Termination (26)') and event_start_dt >= '" + from_date + "' and event_start_dt <= '" + str(pd.to_datetime(date.today())) + "' group by department_unit, department_unit_desc order by count desc"
                df3 = pd.read_sql_query(query, self.hrdata_cnxn())
                cols = ['department_unit', 'department_unit_desc']
                # we create the department column and drop department_unit, department_unit_desc columns
                df3['department'] = df3.apply(lambda r: "{0} ({1})".format(r['department_unit_desc'], r['department_unit']), axis=1)
                df3 = df3.drop(['department_unit', 'department_unit_desc'], 1)

            else:
                query = "SELECT Top 10 count(*) as count, " + criteria1 + "  FROM " + hrdata_table + " where job_tos_is1 in ('1') and event_type_nm in ('Termination (26)') and event_start_dt >= '" + from_date + "' and event_start_dt <= '" + str(pd.to_datetime(date.today())) + "' group by (" + criteria1 + ") order by count desc"
                df3 = pd.read_sql_query(query, self.hrdata_cnxn())

        else:            
            if str(criteria1) == 'cost_center_cd':
                query = "SELECT Top 10 cost_center_cd, cost_center_desc, count(*) as count FROM " + hrdata_table + " where job_tos_is1 in ('1') and event_type_nm in ('Termination (26)') and event_start_dt >= '" + from_date + "' and event_start_dt <= '" + to_date + "' group by cost_center_cd, cost_center_desc order by count desc"
                df3 = pd.read_sql_query(query, self.hrdata_cnxn()) 
                cols = ['cost_center_cd', 'cost_center_desc']
                # we create the cost_center column and drop cost_center_cd, cost_center_desc columns
                df3['cost_center'] = df3.apply(lambda r: "{0} ({1})".format(r['cost_center_desc'], r['cost_center_cd']), axis=1)
                df3 = df3.drop(['cost_center_cd', 'cost_center_desc'], 1)

            elif str(criteria1) == 'department_unit':
                query = "SELECT Top 10 department_unit, department_unit_desc, count(*) as count FROM " + hrdata_table + " where job_tos_is1 in ('1') and event_type_nm in ('Termination (26)') and event_start_dt >= '" + from_date + "' and event_start_dt <= '" + to_date + "' group by department_unit, department_unit_desc order by count desc"
                df3 = pd.read_sql_query(query, self.hrdata_cnxn())
                cols = ['department_unit', 'department_unit_desc']
                # we create the department column and drop department_unit, department_unit_desc columns
                df3['department'] = df3.apply(lambda r: "{0} ({1})".format(r['department_unit_desc'], r['department_unit']), axis=1)
                df3 = df3.drop(['department_unit', 'department_unit_desc'], 1)

            else:
                query = "SELECT Top 10 count(*) as count, " + criteria1 + " FROM " + hrdata_table + " where job_tos_is1 in ('1') and event_type_nm in ('Termination (26)') and event_start_dt >= '" + from_date + "' and event_start_dt <= '" + to_date + "' group by (" + criteria1 + ") order by count desc"
                df3 = pd.read_sql_query(query, self.hrdata_cnxn())
                
        print(dict(df3.values))
        return dict(df3.values)

    # Headcount query related functions
    def headcount_non_terminated(self, criteria1, usertext): 
        # logic for Headcount of Non-terminated employees query...
        if str(criteria1) == 'cost_center_cd':
            query = f"SELECT cost_center_cd, cost_center_desc, count(*) as count from " + hrdata_table + " where job_tos_is1 in ('1') and emplmt_status_desc not in ('Terminated') and cost_center_cd in ('" + usertext + "')  group by cost_center_cd, cost_center_desc"
            df3 = pd.read_sql_query(query, self.hrdata_cnxn())
            return dict({str(df3['count'][0]) : df3['cost_center_desc'][0] + " (" + df3['cost_center_cd'][0] + ")"})
        elif str(criteria1) == 'department_unit':
            query = f"SELECT department_unit, department_unit_desc, count(*) as count from " + hrdata_table + " where job_tos_is1 in ('1') and emplmt_status_desc not in ('Terminated') and department_unit in ('" + usertext + "')  group by department_unit, department_unit_desc"
            df3 = pd.read_sql_query(query, self.hrdata_cnxn())
            return dict({str(df3['count'][0]) : df3['department_unit_desc'][0] + " (" + df3['department_unit'][0] + ")"})
        else:
            query = f"SELECT " + criteria1 + ", count(*) as count FROM " + hrdata_table + " where job_tos_is1 in ('1') and emplmt_status_desc not in ('Terminated') and " + criteria1 + " in ('" + usertext + "') group by (" + criteria1 + ")"
            df3 = pd.read_sql_query(query, self.hrdata_cnxn())
            return dict({str(df3['count'][0]) : df3[criteria1][0]})

    def headcount_hires_by_hiredate(self, criteria1, from_date, to_date, usertext: str):
        # logic for No.of hires by hire date query...
        # since, to_date is optional to enter in adpative card, there are two cases as follows...
        # to_date is either empty or to_date is a date...
        if to_date == "":
            if str(criteria1) == 'cost_center_cd':
                try:
                    query = f"SELECT cost_center_cd, cost_center_desc, count(*) as count FROM " + hrdata_table + " where job_tos_is1 in ('1') and event_type_nm in ('Hire (H)') and event_start_dt >= '" + from_date + "' and event_start_dt <= '" + str(pd.to_datetime(date.today())) + "' and cost_center_cd in ('" + usertext + "') group by cost_center_cd, cost_center_desc"
                    df3 = pd.read_sql_query(query, self.hrdata_cnxn())
                    return dict({str(df3['count'][0]) : df3['cost_center_desc'][0] + " (" + df3['cost_center_cd'][0] + ")"})
                except:
                    print("No Records")
                    return {}
            elif str(criteria1) == 'department_unit':
                try:
                    query = f"SELECT department_unit, department_unit_desc, count(*) as count FROM " + hrdata_table + " where job_tos_is1 in ('1') and event_type_nm in ('Hire (H)') and event_start_dt >= '" + from_date + "' and event_start_dt <= '" + str(pd.to_datetime(date.today())) + "' and department_unit in ('" + usertext + "') group by department_unit, department_unit_desc"
                    df3 = pd.read_sql_query(query, self.hrdata_cnxn())
                    return dict({str(df3['count'][0]) : df3['department_unit_desc'][0] + " (" + df3['department_unit'][0] + ")"})
                except:
                    print("No Records")
                    return {}
            else:
                try:
                    query = f"SELECT " + criteria1 + ", count(*) as count FROM " + hrdata_table + " where job_tos_is1 in ('1') and event_type_nm in ('Hire (H)') and event_start_dt >= '" + from_date + "' and event_start_dt <= '" + str(pd.to_datetime(date.today())) + "' and " + criteria1 + " in ('" + usertext + "') group by (" + criteria1 + ")"
                    df3 = pd.read_sql_query(query, self.hrdata_cnxn())
                    return dict({df3['count'][0]:df3[criteria1][0]})
                except:
                    print("No Records")
                    return {}
        else:      
            if str(criteria1) == 'cost_center_cd':
                try:
                    query = f"SELECT cost_center_cd, cost_center_desc, count(*) as count FROM " + hrdata_table + " where job_tos_is1 in ('1') and event_type_nm in ('Hire (H)') and event_start_dt >= '" + from_date + "' and event_start_dt <= '" + to_date + "' and cost_center_cd in ('" + usertext + "') group by cost_center_cd, cost_center_desc"
                    df3 = pd.read_sql_query(query, self.hrdata_cnxn())

                    return dict({str(df3['count'][0]) : df3['cost_center_desc'][0] + " (" + df3['cost_center_cd'][0] + ")"})
                except:
                    print("No Records")
                    return {}
            elif str(criteria1) == 'department_unit':
                try:
                    query = f"SELECT department_unit, department_unit_desc, count(*) as count FROM " + hrdata_table + " where job_tos_is1 in ('1') and event_type_nm in ('Hire (H)') and event_start_dt >= '" + from_date + "' and event_start_dt <= '" + to_date + "' and department_unit in ('" + usertext + "') group by department_unit, department_unit_desc"
                    df3 = pd.read_sql_query(query, self.hrdata_cnxn())
                    return dict({str(df3['count'][0]) : df3['department_unit_desc'][0] + " (" + df3['department_unit'][0] + ")"})
                except:
                    print("No Records")
                    return {}
            else:
                try:
                    query = f"SELECT " + criteria1 + ", count(*) as count FROM " + hrdata_table + " where job_tos_is1 in ('1') and event_type_nm in ('Hire (H)') and event_start_dt >= '" + from_date + "' and event_start_dt <= '" + to_date + "' and " + criteria1 + " in ('" + usertext + "') group by (" + criteria1 + ")"
                    df3 = pd.read_sql_query(query, self.hrdata_cnxn())
                    return dict({df3['count'][0]:df3[criteria1][0]})
                except:
                    print("No Records")    
                    return {}

    def headcount_trmns_by_terminationdate(self, criteria1, from_date, to_date, usertext: str):
        # logic for No.of terminations by termination date query...
        # since, to_date is optional to enter in adpative card, there are two cases as follows...
        # to_date is either empty or to_date is a date...
        if to_date == "":
            if str(criteria1) == 'cost_center_cd':
                try:
                    query = f"SELECT cost_center_cd, cost_center_desc, count(*) as count FROM " + hrdata_table + " where job_tos_is1 in ('1') and event_type_nm in ('Termination (26)') and event_start_dt >= '" + from_date + "' and event_start_dt <= '" + str(pd.to_datetime(date.today())) + "' and cost_center_cd in ('" + usertext + "') group by cost_center_cd, cost_center_desc"
                    df3 = pd.read_sql_query(query, self.hrdata_cnxn())
                    return dict({str(df3['count'][0]) : df3['cost_center_desc'][0] + " (" + df3['cost_center_cd'][0] + ")"})
                except:
                    print("No Records")
                    return {}
            elif str(criteria1) == 'department_unit':
                try:
                    query = f"SELECT department_unit, department_unit_desc, count(*) as count FROM " + hrdata_table + " where job_tos_is1 in ('1') and event_type_nm in ('Termination (26)') and event_start_dt >= '" + from_date + "' and event_start_dt <= '" + str(pd.to_datetime(date.today())) + "' and department_unit in ('" + usertext + "') group by department_unit, department_unit_desc"
                    df3 = pd.read_sql_query(query, self.hrdata_cnxn())
                    return dict({str(df3['count'][0]) : df3['department_unit_desc'][0] + " (" + df3['department_unit'][0] + ")"})
                except:
                    print("No Records")
                    return {}
            else:
                try:
                    query = f"SELECT " + criteria1 + ", count(*) as count FROM " + hrdata_table + " where job_tos_is1 in ('1') and event_type_nm in ('Termination (26)') and event_start_dt >= '" + from_date + "' and event_start_dt <= '" + str(pd.to_datetime(date.today())) + "' and " + criteria1 + " in ('" + usertext + "') group by (" + criteria1 + ")"
                    df3 = pd.read_sql_query(query, self.hrdata_cnxn())
                    return dict({df3['count'][0]:df3[criteria1][0]})
                except:
                    print("No Records")
                    return {}
        else:      
            if str(criteria1) == 'cost_center_cd':
                try:
                    query = f"SELECT cost_center_cd, cost_center_desc, count(*) as count FROM " + hrdata_table + " where job_tos_is1 in ('1') and event_type_nm in ('Termination (26)') and event_start_dt >= '" + from_date + "' and event_start_dt <= '" + to_date + "' and cost_center_cd in ('" + usertext + "') group by cost_center_cd, cost_center_desc"
                    df3 = pd.read_sql_query(query, self.hrdata_cnxn())
                    return dict({str(df3['count'][0]) : df3['cost_center_desc'][0] + " (" + df3['cost_center_cd'][0] + ")"})
                except:
                    print("No Records")
                    return {}
            elif str(criteria1) == 'department_unit':
                try:
                    query = f"SELECT department_unit, department_unit_desc, count(*) as count FROM " + hrdata_table + " where job_tos_is1 in ('1') and event_type_nm in ('Termination (26)') and event_start_dt >= '" + from_date + "' and event_start_dt <= '" + to_date + "' and department_unit in ('" + usertext + "') group by department_unit, department_unit_desc"
                    df3 = pd.read_sql_query(query, self.hrdata_cnxn())
                    return dict({str(df3['count'][0]) : df3['department_unit_desc'][0] + " (" + df3['department_unit'][0] + ")"})
                except:
                    print("No Records")
                    return {}
            else:
                try:
                    query = f"SELECT " + criteria1 + ", count(*) as count FROM " + hrdata_table + " where job_tos_is1 in ('1') and event_type_nm in ('Termination (26)') and event_start_dt >= '" + from_date + "' and event_start_dt <= '" + to_date + "' and " + criteria1 + " in ('" + usertext + "') group by (" + criteria1 + ")"
                    df3 = pd.read_sql_query(query, self.hrdata_cnxn())
                    return dict({df3['count'][0]:df3[criteria1][0]})
                except:
                    print("No Records")     
                    return {}           

    # The below 3 methods are for headcount choice, when the 2nd choice is None criteria
    def headcount_None_nonterminated(self): 
        query = "select count(*) as count from " + hrdata_table + " where job_tos_is1 in ('1') and emplmt_status_desc not in ('Terminated')"
        df3 = pd.read_sql_query(query, self.hrdata_cnxn())
        print(dict({"count" : df3['count'][0]}) )
        return dict({"count" : str(df3['count'][0])})

    def headcount_None_hire(self, from_date, to_date):
        # since, to_date is optional to enter in adpative card, there are two cases as follows...
        # to_date is either empty or to_date is a date...      
        if to_date == "":
            query = f"SELECT count(*) as count FROM " + hrdata_table + " where job_tos_is1 in ('1') and event_type_nm in ('Hire (H)') and event_start_dt >= '" + from_date + "' and event_start_dt <= '" + str(pd.to_datetime(date.today())) + "' "
            df3 = pd.read_sql_query(query, self.hrdata_cnxn())
            return dict({"count" : str(df3['count'][0])})           
        else:
            query = f"SELECT count(*) as count FROM " + hrdata_table + " where job_tos_is1 in ('1') and event_type_nm in ('Hire (H)') and event_start_dt >= '" + from_date + "' and event_start_dt <= '" + to_date + "' "
            df3 = pd.read_sql_query(query, self.hrdata_cnxn())
            return dict({"count" : str(df3['count'][0])})

    def headcount_None_terminated(self, from_date, to_date): 
        # since, to_date is optional to enter in adpative card, there are two cases as follows...
        # to_date is either empty or to_date is a date...           
        if to_date == "":
            query = f"SELECT count(*) as count FROM " + hrdata_table + " where job_tos_is1 in ('1') and event_type_nm in ('Termination (26)') and event_start_dt >= '" + from_date + "' and event_start_dt <= '" + str(pd.to_datetime(date.today())) + "' "
            df3 = pd.read_sql_query(query, self.hrdata_cnxn())
            return dict({"count" : str(df3['count'][0])})           
        else:
            query = f"SELECT count(*) as count FROM " + hrdata_table + " where job_tos_is1 in ('1') and event_type_nm in ('Termination (26)') and event_start_dt >= '" + from_date + "' and event_start_dt <= '" + to_date + "' "
            df3 = pd.read_sql_query(query, self.hrdata_cnxn())
            return dict({"count" : str(df3['count'][0])})

    def validate_headcount_text(self, usertext):
        # This method is to validate the text value entered by user in text box of adaptive card in Headcount query...
        # The below 8 try except statements are to check whether the value entered is a valid cost_center_cd or department_unit or division_nm or location_cd or md_name or rptg_wrkgrp or sr_vp_name or vp_name
        try:
            if pd.read_sql_query(f"SELECT count(*) as count FROM " + hrdata_table + " where job_tos_is1 in ('1') and cost_center_cd in ('" + usertext + "') ", self.hrdata_cnxn())['count'][0] > 0:
                print(pd.read_sql_query(f"SELECT count(*) as count FROM " + hrdata_table + " where job_tos_is1 in ('1') and cost_center_cd in ('" + usertext + "') ", self.hrdata_cnxn())['count'][0])
                return True
            else:
                pass
        except:
            pass

        try:
            if pd.read_sql_query(f"SELECT count(*) as count FROM " + hrdata_table + " where job_tos_is1 in ('1') and department_unit in ('" + usertext + "') ", self.hrdata_cnxn())['count'][0] > 0:
                print(pd.read_sql_query(f"SELECT count(*) as count FROM " + hrdata_table + " where job_tos_is1 in ('1') and department_unit in ('" + usertext + "') ", self.hrdata_cnxn())['count'][0])
                return True
            else:
                pass
        except:
            pass

        try:
            if pd.read_sql_query(f"SELECT count(*) as count FROM " + hrdata_table + " where job_tos_is1 in ('1') and division_nm in ('" + usertext + "') ", self.hrdata_cnxn())['count'][0] > 0:
                print(pd.read_sql_query(f"SELECT count(*) as count FROM " + hrdata_table + " where job_tos_is1 in ('1') and division_nm in ('" + usertext + "') ", self.hrdata_cnxn())['count'][0])
                return True
            else:
                pass
        except:
            pass

        try:
            if pd.read_sql_query(f"SELECT count(*) as count FROM " + hrdata_table + " where job_tos_is1 in ('1') and location_cd in ('" + usertext + "') ", self.hrdata_cnxn())['count'][0] > 0:
                print(pd.read_sql_query(f"SELECT count(*) as count FROM " + hrdata_table + " where job_tos_is1 in ('1') and location_cd in ('" + usertext + "') ", self.hrdata_cnxn())['count'][0])
                return True
            else:
                pass
        except:
            pass

        try:
            print("md_name")
            if pd.read_sql_query(f"SELECT count(*) as count FROM " + hrdata_table + " where job_tos_is1 in ('1') and md_name in ('" + usertext + "') ", self.hrdata_cnxn())['count'][0] > 0:
                print(pd.read_sql_query(f"SELECT count(*) as count FROM " + hrdata_table + " where job_tos_is1 in ('1') and md_name in ('" + usertext + "') ", self.hrdata_cnxn())['count'][0])
                return True
            else:
                pass
        except:
            pass

        try:
            if pd.read_sql_query(f"SELECT count(*) as count FROM " + hrdata_table + " where job_tos_is1 in ('1') and rptg_wrkgrp in ('" + usertext + "') ", self.hrdata_cnxn())['count'][0] > 0:
                print(pd.read_sql_query(f"SELECT count(*) as count FROM " + hrdata_table + " where job_tos_is1 in ('1') and rptg_wrkgrp in ('" + usertext + "') ", self.hrdata_cnxn())['count'][0])
                return True
            else:
                pass
        except:
            pass

        try:
            if pd.read_sql_query(f"SELECT count(*) as count FROM " + hrdata_table + " where job_tos_is1 in ('1') and sr_vp_name in ('" + usertext + "') ", self.hrdata_cnxn())['count'][0] > 0:
                print(pd.read_sql_query(f"SELECT count(*) as count FROM " + hrdata_table + " where job_tos_is1 in ('1') and sr_vp_name in ('" + usertext + "') ", self.hrdata_cnxn())['count'][0])
                return True
            else:
                pass
        except:
            pass

        try:
            if pd.read_sql_query(f"SELECT count(*) as count FROM " + hrdata_table + " where job_tos_is1 in ('1') and vp_name in ('" + usertext + "') ", self.hrdata_cnxn())['count'][0] > 0:
                print(pd.read_sql_query(f"SELECT count(*) as count FROM " + hrdata_table + " where job_tos_is1 in ('1') and vp_name in ('" + usertext + "') ", self.hrdata_cnxn())['count'][0])
                return True
            else:
                print("False")
                return False
        except:
            return False



    def validate_rqstn_id(self, rqstn_id: int):
        # This method is to validate whether the requisition id entered is present in the database or not...
        print(pd.read_sql_query(f"SELECT count(*) as count FROM " + hiringdata_table + " where job_rqstn_id in ('" + str(rqstn_id) + "')", self.hiringdata_cnxn())['count'][0] > 0)
        return (pd.read_sql_query(f"SELECT count(*) as count FROM " + hiringdata_table + " where job_rqstn_id in ('" + str(rqstn_id) + "')", self.hiringdata_cnxn())['count'][0] > 0)

    def hiringdata_details(self, rqstn_id: int):
        # This method returns the requisition details based on the requisition id entered by the user. 
        df1 = pd.read_sql_query(f"SELECT * FROM " + hiringdata_table + " where job_rqstn_id in ('" + str(rqstn_id) + "')", self.hiringdata_cnxn()) 
        response = {}
        response['rqstn_id'] = df1[df1['job_rqstn_id']==rqstn_id]['job_rqstn_id'].values[0]
        response['hire_mgr'] = df1[df1['job_rqstn_id']==rqstn_id]['hire_mgr'].values[0]
        response['aprvl_dt'] = df1[df1['job_rqstn_id']==rqstn_id]['aprvl_dt'].values[0]
        response['job_rqstn_status'] = df1[df1['job_rqstn_id']==rqstn_id]['rqstn_status'].values[0]
        response['job_title'] = df1[df1['job_rqstn_id']==rqstn_id]['job_title'].values[0]
        response['age_of_rqsnt'] = df1[df1['job_rqstn_id']==rqstn_id]['age_of_rqstn'].values[0]
        response['nbr_of_openings'] = df1[df1['job_rqstn_id']==rqstn_id]['nbr_of_openings'].values[0]

        return response

    def hiringdata_countofrqstn(self, criteria1, criteria2):
        # This method returns the count of requisitions by applications status based on the criteria...
        # This is a count of requisitions query...
        try:
            df3 = pd.read_sql_query(f"SELECT Top 10 " + criteria2 + ", count(*) as count FROM " + hiringdata_table + " where rqstn_status in ('" + criteria1 + "') group by (" + criteria2 + ")", self.hiringdata_cnxn())
            print(dict(df3.values))
            return dict(df3.values)
        except:
            print("No Records")     
            return {}

    def validate_appl_status_text(self, usertext):
        # This method is to validate the usertext entered in the text box of adaptive card...
        # The below 9 try except statements are to check whether the value entered is a valid md_name or vp_name or svp_name or svp2_name or svp3_name or job_division or job_catg or work_loc or evp_name
        try:
            if pd.read_sql_query(f"SELECT count(*) as count FROM " + hiringappl_table + " where md_name in ('" + usertext + "') ", self.hiringdata_cnxn())['count'][0] > 0:
                print(pd.read_sql_query(f"SELECT count(*) as count FROM " + hiringappl_table + " where md_name in ('" + usertext + "') ", self.hiringdata_cnxn())['count'][0])
                return True
            else:
                pass
        except:
            return False

        try:
            if pd.read_sql_query(f"SELECT count(*) as count FROM " + hiringappl_table + " where vp_name in ('" + usertext + "') ", self.hiringdata_cnxn())['count'][0] > 0:
                print(pd.read_sql_query(f"SELECT count(*) as count FROM " + hiringappl_table + " where vp_name in ('" + usertext + "') ", self.hiringdata_cnxn())['count'][0])
                return True
            else:
                pass
        except:
            return False

        try:
            if pd.read_sql_query(f"SELECT count(*) as count FROM " + hiringappl_table + " where svp_name in ('" + usertext + "') ", self.hiringdata_cnxn())['count'][0] > 0:
                print(pd.read_sql_query(f"SELECT count(*) as count FROM " + hiringappl_table + " where svp_name in ('" + usertext + "') ", self.hiringdata_cnxn())['count'][0])
                return True
            else:
                pass
        except:
            return False

        try:
            if pd.read_sql_query(f"SELECT count(*) as count FROM " + hiringappl_table + " where svp2_name in ('" + usertext + "') ", self.hiringdata_cnxn())['count'][0] > 0:
                print(pd.read_sql_query(f"SELECT count(*) as count FROM " + hiringappl_table + " where svp2_name in ('" + usertext + "') ", self.hiringdata_cnxn())['count'][0])
                return True
            else:
                pass
        except:
            return False

        try:
            if pd.read_sql_query(f"SELECT count(*) as count FROM " + hiringappl_table + " where svp3_name in ('" + usertext + "') ", self.hiringdata_cnxn())['count'][0] > 0:
                print(pd.read_sql_query(f"SELECT count(*) as count FROM " + hiringappl_table + " where svp3_name in ('" + usertext + "') ", self.hiringdata_cnxn())['count'][0])
                return True
            else:
                pass
        except:
            return False

        try:
            if pd.read_sql_query(f"SELECT count(*) as count FROM " + hiringappl_table + " where job_division in ('" + usertext + "') ", self.hiringdata_cnxn())['count'][0] > 0:
                print(pd.read_sql_query(f"SELECT count(*) as count FROM " + hiringappl_table + " where job_division in ('" + usertext + "') ", self.hiringdata_cnxn())['count'][0])
                return True
            else:
                pass
        except:
            return False

        try:
            if pd.read_sql_query(f"SELECT count(*) as count FROM " + hiringappl_table + " where job_catg in ('" + usertext + "') ", self.hiringdata_cnxn())['count'][0] > 0:
                print(pd.read_sql_query(f"SELECT count(*) as count FROM " + hiringappl_table + " where job_catg in ('" + usertext + "') ", self.hiringdata_cnxn())['count'][0])
                return True
            else:
                pass
        except:
            return False

        try:
            if pd.read_sql_query(f"SELECT count(*) as count FROM " + hiringappl_table + " where work_loc in ('" + usertext + "') ", self.hiringdata_cnxn())['count'][0] > 0:
                print(pd.read_sql_query(f"SELECT count(*) as count FROM " + hiringappl_table + " where work_loc in ('" + usertext + "') ", self.hiringdata_cnxn())['count'][0])
                return True
            else:
                pass
        except:
            return False

        try:
            if pd.read_sql_query(f"SELECT count(*) as count FROM " + hiringappl_table + " where evp_name in ('" + usertext + "') ", self.hiringdata_cnxn())['count'][0] > 0:
                print(pd.read_sql_query(f"SELECT count(*) as count FROM " + hiringappl_table + " where evp_name in ('" + usertext + "') ", self.hiringdata_cnxn())['count'][0])
                return True
            else:
                print("False")
                return False
        except:
            return False

    # This method is for application status query on application data...
    # It returns the Top 10 application status records
    def hiringdata_application_status(self, criteria, usertext, from_date, to_date):
        if to_date == "":
            df3 = pd.read_sql_query(f"select Top 10 count(*) as count, application_status from " + hiringappl_table + " where " + criteria + " in ('" + usertext + "') and application_dt >= '" + from_date + "' and application_dt <= '" + str(pd.to_datetime(date.today())) + "' and is_tos in ('TRUE') group by application_status order by count desc", self.hiringdata_cnxn())
        else:
            df3 = pd.read_sql_query(f"select Top 10 count(*) as count, application_status from " + hiringappl_table + " where " + criteria + " in ('" + usertext + "') and application_dt >= '" + from_date + "' and application_dt <= '" + to_date + "' and is_tos in ('TRUE') group by application_status order by count desc", self.hiringdata_cnxn())

        print(dict(df3.values))
        return dict(df3.values)

    # This method is for application status query on application data when the chosen criteria is None...
    # It returns the Top 10 application status records
    def hiringdata_application_status_None(self, from_date, to_date):
        if to_date == "":
            df3 = pd.read_sql_query(f"select Top 10 count(*) as count, application_status from " + hiringappl_table + " where application_dt >= '" + from_date + "' and application_dt <= '" + str(pd.to_datetime(date.today())) + "' and is_tos in ('TRUE') group by application_status order by count desc", self.hiringdata_cnxn())
        else:
            df3 = pd.read_sql_query(f"select Top 10 count(*) as count, application_status from " + hiringappl_table + " where application_dt >= '" + from_date + "' and application_dt <= '" + to_date + "' and is_tos in ('TRUE') group by application_status order by count desc", self.hiringdata_cnxn())

        print(dict(df3.values))
        return dict(df3.values)