class BlueprintComponent < ApplicationRecord

  JITA_EVE_SYSTEM_ID=30000142
  JITA_REGION_CPP_ID=10000002

  has_many :blueprint_materials
  has_many :blueprints, through: :blueprint_materials

  def self.set_min_prices_for_all_components

    Banner.p 'Recomputing costs from Jita prices'

    trade_hub_id = TradeHub.find_by_eve_system_id( JITA_EVE_SYSTEM_ID ).id

    BlueprintComponent.all.each do |component|
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
end
