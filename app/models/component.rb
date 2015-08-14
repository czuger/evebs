class Component < ActiveRecord::Base
  JITA_EVE_SYSTEM_ID=30000142

  validates :cpp_eve_item_id, :name, presence: true
  extend MultiplePriceRetriever

  has_many :materials
  has_many :blueprints, through: :materials
  has_many :eve_items, through: :blueprints
  has_many :users, through: :eve_items

  def self.used_components
    used_items = EveItem.used_items
    used_components = []
    used_items.each do |item|
      item.components.each do |component|
        used_components << component unless used_components.include?( component )
      end
    end
    used_components
  end

  def self.set_avg_prices_for_all_components
    component_ids = Component.all.to_a.map{ |c| c.cpp_eve_item_id }
    result = get_prices( JITA_EVE_SYSTEM_ID, component_ids, 'avg' )
    result.each_pair do |key,value|
      # puts key, value
      component = Component.find_by_cpp_eve_item_id( key )
      component.update_attribute( :cost, value )
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
