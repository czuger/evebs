require 'open-uri'
require 'open-uri/cached'
require 'pp'

class EveItem < ActiveRecord::Base

  include Assert
  include ItemsInit::ItemSetupAndComp
  extend ItemsInit::ItemSetupAndCompSelf
  extend MultiplePriceRetriever

  has_and_belongs_to_many :users
  has_one :blueprint, dependent: :destroy
  has_many :materials, through: :blueprint
  has_many :components, through: :materials
  belongs_to :market_group
  has_many :crest_price_histories, dependent: :destroy
  has_many :crest_prices_last_month_averages, dependent: :destroy

  # Itemps containing non ascii characters
  UNPROCESSABLE_ITEMS=[34457,34458,34459,34460,34461,34462,34463,34464,34465,34466,34467,34468,34469,34470,34471,34472,
                       34473,34474,34475,34476,34477,34478,34479,34480,30952,32371,32372]

  AVG_INDUSTRY_TAX = 0.11 # 10 % base + 1 % system costs (assuming players are smart enough to go in low cost systems)

  def self.to_eve_item_id(cpp_eve_item_id)
    eve_item=EveItem.where( 'cpp_eve_item_id=?', cpp_eve_item_id).first
    eve_item ? eve_item.id : nil
  end

  def self.used_items
    used_items, dummy = User.get_used_items_and_trade_hubs
    used_items
  end

  def single_unit_cost
    (cost*(1+AVG_INDUSTRY_TAX))/blueprint.prod_qtt if cost && blueprint
  end

  def pcent_margin( price )
    (price / single_unit_cost)-1 if price && single_unit_cost
  end

  def margin( price )
    price - single_unit_cost if price && single_unit_cost
  end

  def full_batch_size
    blueprint.nb_runs*blueprint.prod_qtt if blueprint
  end

  # Dead code
  #
  # def compute_min_price_for_system(system)
  #   # For now, we no more use the min price, but the avg prices
  #   # Method keep the old name, to avoid huge code refactoring
  #
  #   min = get_min_price_from_eve_central(cpp_eve_item_id,system.eve_system_id)
  #
  #   min_price_item = MinPrice.where( 'eve_item_id = ? AND trade_hub_id = ?', id, system.id ).first
  #
  #   if min
  #     set_min_price_for_system(min,system.id)
  #   else
  #     # We no more destroy the item
  #     # if min_price_item
  #     #   puts "Destroying min price for item : #{min_price_item.inspect}"
  #     #   min_price_item.destroy
  #     # end
  #   end
  # end

end
