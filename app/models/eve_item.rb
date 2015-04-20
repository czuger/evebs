require 'open-uri'
require 'open-uri/cached'
require 'pp'

OpenURI::Cache.cache_path = 'tmp'

class EveItem < ActiveRecord::Base

  include MinPriceRetriever

  has_and_belongs_to_many :users
  has_one :blueprint
  has_many :materials, through: :blueprint
  has_many :components, through: :materials

  def self.to_eve_item_id(cpp_eve_item_id)
    eve_item=EveItem.where( 'cpp_eve_item_id=?', cpp_eve_item_id).first
    eve_item ? eve_item.id : nil
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
    update_attribute(:cost,total_cost)
  end

  def set_min_price(system)
    min = get_min_price_from_eve_central(cpp_eve_item_id,system.eve_system_id)
    min_price_item = MinPrice.where( 'eve_item_id = ? AND trade_hub_id = ?', id, system.id ).first
    if min
      unless min_price_item
        MinPrice.create!( eve_item: self, trade_hub: system, min_price: min )
      else
        min_price_item.update_attribute( :min_price, min )
      end
    else
      if min_price_item
        min_price_item.destroy
      end
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
        item_list << [key.to_i,value]
      end
    end
    item_list.shift(2)
    item_list.pop(3)
    Hash[item_list]
  end

end
