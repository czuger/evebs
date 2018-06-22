# require 'open-uri'
# # require 'open-uri/cached'
require 'pp'

class EveItem < ApplicationRecord

  include Assert

  has_and_belongs_to_many :users
  has_one :blueprint, dependent: :destroy
  has_many :materials, through: :blueprint
  has_many :components, through: :materials
  belongs_to :market_group
  has_many :eve_markets_histories, dependent: :destroy
  has_many :crest_prices_last_month_averages, dependent: :destroy

  has_many :prices_advices
  has_many :prices_mins

  def self.to_eve_item_id(cpp_eve_item_id)
    eve_item=EveItem.where( 'cpp_eve_item_id=?', cpp_eve_item_id).first
    eve_item ? eve_item.id : nil
  end

  def self.used_items
    used_items, dummy = User.get_used_items_and_trade_hubs
    used_items
  end

  # Recompute the cost for all items
  def self.compute_cost_for_all_items
    Component.set_min_prices_for_all_components

    Banner.p 'Refreshing all items costs'
    EveItem.joins( :blueprint ).all.each do |ei|
      # puts "Recomputing cost for #{ei.name}"
      ei.compute_cost
    end

  end

  def compute_cost
    total_cost = 0
    materials.each do |material|
      if material.component.cost
        total_cost += material.component.cost * material.required_qtt
      else
        puts "Warning !!! #{material.component.inspect} has no cost" unless Rails.env == 'test'
        # If we lack a material we set the price to nil and exit
        update_attribute(:cost,nil)
        return
      end
    end
    if total_cost <= 0
      puts "Warning !!! #{self.inspect} has no cost" unless Rails.env == 'test'
      # If we lack a material we set the price to nil and exit
      update_attribute(:cost,nil)
      return
    end
    update_attribute(:cost,total_cost)
  end

end
