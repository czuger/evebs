# require 'open-uri'
# # require 'open-uri/cached'
require 'pp'

class EveItem < ApplicationRecord

  include Assert
  include ItemsInit::ItemSetupAndComp
  extend ItemsInit::ItemSetupAndCompSelf
  extend MultiplePriceRetriever
  # extend Setup::UpdateEveItems

  has_and_belongs_to_many :users
  has_one :blueprint, dependent: :destroy
  has_many :materials, through: :blueprint
  has_many :components, through: :materials
  belongs_to :market_group
  has_many :eve_markets_histories, dependent: :destroy
  has_many :crest_prices_last_month_averages, dependent: :destroy

  has_many :prices_advices

  # TODO : remove this dead code
  # Itemps containing non ascii characters
  # UNPROCESSABLE_ITEMS=[34457,34458,34459,34460,34461,34462,34463,34464,34465,34466,34467,34468,34469,34470,34471,34472,
  #                      34473,34474,34475,34476,34477,34478,34479,34480,30952,32371,32372]
  #
  # AVG_INDUSTRY_TAX = 0.11 # 10 % base + 1 % system costs (assuming players are smart enough to go in low cost systems)

  def self.to_eve_item_id(cpp_eve_item_id)
    eve_item=EveItem.where( 'cpp_eve_item_id=?', cpp_eve_item_id).first
    eve_item ? eve_item.id : nil
  end

  def self.used_items
    used_items, dummy = User.get_used_items_and_trade_hubs
    used_items
  end

  # TODO : remove this dead code
  # # def single_unit_cost
  # #   (cost*(1+AVG_INDUSTRY_TAX))/blueprint.prod_qtt if cost && blueprint
  # # end
  # #
  # # def pcent_margin( price )
  # #   (price / single_unit_cost)-1 if price && single_unit_cost
  # # end
  # #
  # # def margin( price )
  # #   price - single_unit_cost if price && single_unit_cost
  # # end
  #
  # def full_batch_size
  #   unless blueprint
  #     puts "EveItem#full_batch_size : #{self.inspect} has no blueprint"
  #     return -Float::INFINITY
  #   end
  #   blueprint.nb_runs*blueprint.prod_qtt
  # end

end
