from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Float, BigInteger
from sqlalchemy.orm import relationship
# from fastapi_utils.guid_type import GUID
#from pydantic import List
from database import Base

## code examples 
# id = Column(Integer, primary_key=True, index=True)
# email = Column(String, unique=True, index=True)
# hashed_password = Column(String)
# is_active = Column(Boolean, default=True)
# items = relationship("Item", back_populates="owner")


#### BASE TABLES (INITIAL INGESTION)
class CampaignDesc(Base):
    __tablename__ = "campaign_desc"
    index = Column(Integer, primary_key=True, autoincrement=True, nullable=False, index=True)
    campaign = Column(Integer)#, unique=True)
    description =  Column(String)
    end_day = Column(Integer) # this table has values from 1-700+, not datetime.. yet.
    start_day = Column(Integer)

    # def __repr__(self):
    #     return f"Campaign Description for Campaign {self.campaign}"

class CampaignTable(Base):
    __tablename__ = "campaign_table"
    index = Column(Integer, primary_key=True, autoincrement=True, nullable=False, index=True)
    campaign = Column(Integer)
    description = Column(String)
    household_key = Column(Integer)#, ForeignKey("hh_demographic.household_key"))
    ####
    #hh_demographic = relationship("HHDemographic")
    #coupons = relationship('Coupon')

    # def __repr__(self):
    #     return f"Household {self.household_key} was targeted by the {self.description} campaign, number {self.campaign}"



class CausalData(Base):
    __tablename__ = "causal_data"
    index = Column(Integer, primary_key=True, autoincrement=True, nullable=False, index=True)
    product_id = Column(Integer)#, ForeignKey('product.product_id'))
    store_id = Column(Integer)
    week_no = Column(Integer)
    display = Column(String)
    mailer = Column(String)
    ###
    #products = relationship("Product")


class Coupon(Base):
    __tablename__ = "coupon"
    index = Column(Integer, primary_key=True, autoincrement=True, nullable=False, index=True)
    campaign = Column(Integer)#, ForeignKey('campaign_desc.campaign'))
    coupon_upc = Column(BigInteger)#, unique=True)
    product_id = Column(BigInteger)#, ForeignKey('product.product_id'))
    # products = relationship("Product")


class CouponRedempt(Base):
    __tablename__ = "coupon_redempt"
    index = Column(Integer, primary_key=True, autoincrement=True, nullable=False, index=True)
    campaign = Column(Integer)#, ForeignKey('campaign_desc.campaign'))
    coupon_upc = Column(BigInteger)
    day = Column(Integer)
    household_key = Column(Integer)#, ForeignKey("hh_demographic.household_key"))
    # hh_demographic = relationship("HHDemographic")
    # campaigns = relationship("CampaignDesc")
    #coupons = relationship("Coupon")
    
    # def __repr__(self):
    #     return f"Redeemed Coupon {self.coupon_upc} for campaign {self.campaign}; household {self.household_key}"

class HHDemographic(Base):
    __tablename__ = "hh_demographic"
    index = Column(Integer, primary_key = True, autoincrement=True, nullable=False, index=True)
    age_desc = Column(String)
    hh_comp_desc = Column(String)
    homeowner_desc = Column(String)
    household_key = Column(Integer, unique=True)
    household_size_desc = Column(String)
    income_desc = Column(String)
    kid_category_desc = Column(String)
    marital_status_code = Column(String)

    # def __repr__(self):
    #     return f"Household {self.household_key}"

class Product(Base):
    __tablename__ = "product"
    index = Column(Integer, primary_key=True, autoincrement=True, nullable=False, index=True)
    product_id = Column(BigInteger, unique=True)
    manufacturer = Column(String)
    department = Column(String)
    brand = Column(String)
    commodity_desc = Column(String)
    sub_commodity_desc = Column(String)
    curr_size_of_product = Column(String)

    #campaigns = relationship("CampaignTable")
    #products = relationship("Product")


class TransactionData(Base):
    __tablename__ = "transaction_data"
    index = Column(Integer, primary_key=True, autoincrement=True, nullable=False, index=True)
    household_key = Column(Integer)#, ForeignKey("hh_demographic.household_key"))
    basket_id = Column(BigInteger)
    day = Column(Integer)
    product_id = Column(BigInteger)#, ForeignKey('product.product_id'))
    quantity =  Column(Integer)
    sales_value =  Column(Float)
    store_id =  Column(Integer)
    retail_disc = Column(Float) 
    trans_time =  Column(Integer)
    week_no = Column(Integer)
    coupon_disc = Column(Float) 
    coupon_match_disc = Column(Float)



#### GOLD TIER TABLES (CREATED BY CRON JOBS)
class HHSummary(Base):
    """
    this table will serve as a summary of the existing, static, data; available for easy access for each session with respective household_key/customer id

    while the scope of this use case doesn't include allowing customers to register themselves and make new purchases through the front-end/API;
    this table would be the summary generated by the instantiation of the update/migration cron job, after the primary data extract process
    """
    __tablename__ = 'hh_summary'
    index = Column(Integer, primary_key=True, autoincrement=True, nullable=False, index=True)
    household_key = Column(Integer)

    # demographic info
    age_45_plus = Column(Boolean)
    income_50K_plus = Column(Boolean)
    single_couple_family = Column(Integer)
    has_kids = Column(Boolean)
    single = Column(Boolean)
    couple = Column(Boolean)
    
    # purchases information
        # customer value scores
    r_score = Column(Integer)
    f_score = Column(Integer)
    m_score = Column(Integer)
    rfm_score = Column(Integer)
    rfm_bins = Column(Integer)

        # sales by section
    alcohol = Column(Float)
    beverages = Column(Float)
    concessions = Column(Float)
    dairy = Column(Float)
    drug = Column(Float)
    garden = Column(Float)
    grain_goods = Column(Float)
    grocery = Column(Float)
    home_family = Column(Float)
    junk_food = Column(Float)
    kitchen = Column(Float)
    meat = Column(Float)
    misc = Column(Float)
    produce = Column(Float)
    seasonal = Column(Float)
        # total_sales
    total_sales = Column(Float)
    # last_updated = ??

class DailyCampaignSales(Base):

    __tablename__ = 'daily_campaign_sales'
    index = Column(Integer, primary_key=True, autoincrement=True, nullable=False, index=True)
    day = Column(Integer)
    sales_value = Column(Float)
    campaign_id = Column(Integer)


# class RecommenderCache(Base):
#     """
#     Determining the appropriate method to recommend products to different (types of) users is a business question of fundamental importance.

#     this table is for the pre-populated recommendations;
#     depending on the use case and resources available, this process might take other forms; 
#     I've called it a 'cache' because it could be held in memory for the purpose of availability.
    
#     the functionality of this table could also be split among multiple tables, as in one table for each of our recommendation signals/metrics;
    
#     or partitioned/index as a big table in various ways for rapid access.
    
#     """
#     __tablename__ = 'recommender_cache'
#     index = Column(Integer, primary_key=True, autoincrement=True, nullable=False, index=True)
#     household_key = Column(Integer)#, ForeignKey("hh_demographic.household_key"))
#     #product_ids = Column(List[Integer]) # images, etc. would be referenced by product ID
#     product_names = Column(List[String])