
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#plt.style.use('seaborn')

class CampaignsPage():

    def __init__(self, camp_no):
        self.camp_no = camp_no
        self.df = pd.read_csv(f'data/camp_sales/{self.camp_no}_sales.csv')
        self.all_sales = pd.read_csv('data/campaign_sales.csv', index_col=0) # this df is simply 
        self.campaign_summary = pd.read_csv('data/campaign_summary.csv', index_col=0).drop('Listed Products', axis=1)


    def plot_campaign_sales(self):
        '''Plots a chart of campaign sales over time'''
        sales = self.df
        mydict = self.campaign_summary
        camp_no = self.camp_no

        first = mydict['First Day'][camp_no]
        last = mydict['Last Day'][camp_no]
        total_days = mydict['Duration'][camp_no]
        
        ### How Much Data
        trans_max = sales['DAY'].max()
        trans_min = sales['DAY'].min()
        
        fig, ax = plt.subplots(figsize=(32,12)) 

        plt.title(f'Sales for Products Included in Campaign {camp_no}', fontsize=70)
        plt.ylabel(f'Avg. Daily Sales ($)', fontsize=50)
        plt.xlabel('DAY', fontsize=50)    
        plt.xticks(fontsize=40)
        plt.yticks(fontsize=40)
        ax.plot(sales['DAY'], sales['SALES_VALUE'], label='Daily Sales')
        
        plt.axvspan(first, last, alpha=0.2, color='yellow')

        val = mydict['Listed Products Sales During'][camp_no] / (last - first) + 1
        ax.plot((first, last), (val, val) , color='red', lw=3, ls='--', label=f'Avg. during {round(val,2)}')

        divisor = (trans_max - last) + 1
        if divisor < 1:
            divisor = 1
        val = mydict['Listed Products Sales After'][camp_no] / divisor
        ax.plot((last, trans_max), (val, val) , color='blue', lw=3, ls='--', label=f'Avg. after {round(val,2)}')

        val = mydict['Listed Products Sales Before'][camp_no] / (first - trans_min) + 1 
        ax.plot((trans_min, first), (val, val) , color='purple', lw=3, ls='--', label=f'Avg. before {round(val,2)}')

        val = mydict['Listed Products Total Sales'][camp_no] / ((trans_max - trans_min) +1)
        ax.plot((trans_min, trans_max), (val, val) , color='cyan', lw=3, ls='-', label=f'Avg. total {round(val,2)}', alpha=0.5)
        plt.legend(loc='upper left', fontsize=28)
        
        ### PLOTTING
        st.pyplot(fig, clear_figure=True)
        


    # main
    def main(self):
        st.write(f'# Campaign {int(self.camp_no)}')
        self.plot_campaign_sales()

if __name__ =='__main__':
    import streamlit as st

    def choose_camp_no():
        return st.slider('Pick a Campaign', 1, 30) # this must be an integer between 1 and 2500..?

 
    a = CampaignsPage(choose_camp_no())
    a.main()
    st.write(f"""
    **Above you can see the daily sales of items included in the mailer/flyer advertising campaign {a.camp_no}.**""")
    st.write(f"""
    The highlighted section is when the campaign took place -- the red dashed lines indicated the mean daily sales during that period.""")
    st.write(f"""The purple and blue dashed lines are the mean daily sales of those items before and after the campaign; and the cyan dashed line indicates the total mean daily sales for items included in the campaign. """)
    
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
