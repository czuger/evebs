require 'open-uri'
require 'open-uri/cached'
require 'pp'

OpenURI::Cache.cache_path = 'tmp'

class EveItem < ActiveRecord::Base

  include Assert
  extend MultiplePriceRetriever

  has_and_belongs_to_many :users
  has_one :blueprint
  has_many :materials, through: :blueprint
  has_many :components, through: :materials

  # Itemps containing non ascii characters
  UNWANTED_ITEMS=[34457,34458,34459,34460,34461,34462,34463,34464,34465,34466,34467,34468,34469,34470,34471,34472,34473,34474,34475,34476,34477,34478,34479,34480]

  def self.to_eve_item_id(cpp_eve_item_id)
    eve_item=EveItem.where( 'cpp_eve_item_id=?', cpp_eve_item_id).first
    eve_item ? eve_item.id : nil
  end

  def self.used_items
    used_items, dummy = User.get_used_items_and_trade_hubs
    used_items
  end

  def compute_cost
    total_cost = 0
    materials.each do |material|
      if material.component.cost
        total_cost += material.component.cost * material.required_qtt
      else
        puts "Warning !!! #{material.component.inspect} has no cost"
        # If we lack a material we set the price to nil and exit
        update_attribute(:cost,nil)
        return
      end
    end
    if total_cost <= 0
      puts "Warning !!! #{self.inspect} has no cost"
      # If we lack a material we set the price to nil and exit
      update_attribute(:cost,nil)
      return
    end
    update_attribute(:cost,total_cost)
  end

  def self.compute_min_price_for_system(system, items)
    # For now, we no more use the min price, but the avg prices
    # Method keep the old name, to avoid huge code refactoring

    prices = get_prices( system.eve_system_id, items.map{ |e| e.cpp_eve_item_id }, 'min' )

    prices.each do |cpp_item_id,price|
      # We are cheating, the price is avg, but we still use the name min price
      if price # Sometime nobody sell this object
        item = EveItem.find_by_cpp_eve_item_id( cpp_item_id )
        item.set_min_price_for_system(price,system.id)
      end
    end

  end

  def set_min_price_for_system(min_price,system_id)
    assert(min_price, "min_price is nil", self.class, __method__ )
    assert(system_id, "system is nil", self.class, __method__ )

    puts "Updating price for #{name}, price = #{min_price}"

    min_price_item = MinPrice.where( 'eve_item_id = ? AND trade_hub_id = ?', id, system_id ).first
    unless min_price_item
      MinPrice.create!( eve_item: self, trade_hub_id: system_id, min_price: min_price )
    else
      min_price_item.update_attribute( :min_price, min_price )
    end
  end

  # Required for setting up the database
  def self.download_items_hash
    types = {}
    item_list = []
    open( 'http://eve-files.com/chribba/typeid.txt' ) do |file|
      file.readlines.each do |line|
        # pp line
        key = line[0..11]
        value = line[12..-3]
        # types[key.strip]=value.strip if value
        item_list << [key.to_i,value] unless UNWANTED_ITEMS.include?(key.to_i)
      end
    end
    item_list.shift(2)
    item_list.pop(3)
    Hash[item_list]
  end

  # Required for setting up the database
  def self.compute_all_costs
    types = {}
    item_list = []
    open( 'http://eve-files.com/chribba/typeid.txt' ) do |file|
      file.readlines.each do |line|
        # pp line
        key = line[0..11]
        value = line[12..-3]
        # types[key.strip]=value.strip if value
        item_list << [key.to_i,value] unless UNWANTED_ITEMS.include?(key.to_i)
      end
    end
    item_list.shift(2)
    item_list.pop(3)
    Hash[item_list]
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
