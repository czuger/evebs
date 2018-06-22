class Component < ApplicationRecord

  JITA_EVE_SYSTEM_ID=30000142
  JITA_REGION_CPP_ID=10000002


  validates :cpp_eve_item_id, :name, presence: true
  # extend MultiplePriceRetriever

  has_many :materials
  has_many :blueprints, through: :materials
  has_many :eve_items, through: :blueprints
  has_many :users, through: :eve_items

  has_one :eve_item, :primary_key => :cpp_eve_item_id, foreign_key: :cpp_eve_item_id

  def self.set_blueprints_count
    Component.all.each do |component|
      component.update( blueprints_count: component.blueprints.count )
    end
  end

  def self.set_min_prices_for_all_components

    Banner.p 'Recomputing costs from Jita prices'

    trade_hub_id = TradeHub.find_by_eve_system_id( JITA_EVE_SYSTEM_ID ).id

    Component.all.each do |component|
      component_as_eve_item = EveItem.find_by_cpp_eve_item_id( component.cpp_eve_item_id )
      if component_as_eve_item
        price_set = PricesAvgWeek.where( trade_hub_id: trade_hub_id, eve_item_id: component_as_eve_item.id ).first
        if price_set
          # puts "Updating component price for #{component_as_eve_item.name}" unless Rails.env == 'test'
          component.update_attribute( :cost, price_set.price )
        end
      else
        puts "Unable to find EveItem for #{component.inspect}" unless Rails.env == 'test'
      end
    end

  end

  # Dead code
  #
  # def set_min_price
  #   min_price = get_min_price_from_eve_central(cpp_eve_item_id,JITA_EVE_SYSTEM_ID)
  #   if min_price
  #     update_attribute( :cost, min_price )
  #   end
  # end

end
