
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests 

#plt.style.use('seaborn')

class HouseholdAnalytics():
    '''streamlit Implementation class;
    
    simple household-level analytics summary '''
    
    # ACCEPTING INPUTS
    def __init__(self, hh_id):
        self.hh_id = hh_id

        # actions
    def run_me(self):
        '''API must be running before this requests.get() call will work.
        fetches the data for self.hh_id from localhost server, and writes it to streamlit'''
        st.write(f'# Household {int(self.hh_id)}')
        # self.plot_campaign()
        # st.write(self.load_campaign_sales())
        # st.write(self.load_campaign_summary()['Last Day'][self.camp_no])
        res = requests.get(f"http://fastapi-app:80/hh/{self.hh_id}")
        data = res.json()
        # table = pd.DataFrame(data=data.values(), index=data.keys())
        # table = table.drop('index', axis=0)
        # table.T.set_index('household_key')

        st.write(data)
        # self.plot_section_sales()

if __name__ =='__main__':
    
    import streamlit as st

    def enter_hh_id():
        return int(st.text_input('Enter Household ID',value='1'))

 
    a = HouseholdAnalytics(hh_id=enter_hh_id())

    a.run_me()
    # st.write(f"""
    # **Above you can see the daily sales of items included in the mailer/flyer advertising campaign {a.camp_no}.**""")
    # st.write(f"""
    # The highlighted section is when the campaign took place -- the red dashed lines indicated the mean daily sales during that period.""")
    # st.write(f"""The purple and blue dashed lines are the mean daily sales of those items before and after the campaign; and the cyan dashed line indicates the total mean daily sales for items included in the campaign. """)
    
    # def plotting(func,
    #             choice=choice,
    #             resample_rule=resample_rule,
    #             hh_rr_sales=hh_rr_sales,
    #             ):

    #     '''wrapper for st.pyplot call'''
# #                     ## CREATE A FIGURE USING RCPARAMS 
# # TODO: standardize the y (Sales) scale for this graph
    # #     ### Call set of plotting functions, using active fig, ax
    # #     func(fig, ax)
    # #     return fig, ax
    # #     # OPTIONS FOR FIGURE BEFORE CALLING ST.PYPLOT
