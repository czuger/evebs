class User < ActiveRecord::Base
  has_and_belongs_to_many :eve_items
  has_and_belongs_to_many :trade_hubs

  has_many :blueprints, through: :eve_items
  has_many :materials, through: :blueprints
  has_many :components, through: :materials

  def self.get_used_items_and_trade_hubs
    used_item = []
    used_trade_hubs = []
    User.all.to_a.each do |user|
      user.eve_items.each do |eve_item|
        used_item << eve_item unless used_item.include?( eve_item )
      end
      user.trade_hubs.each do |trade_hub|
        used_trade_hubs << trade_hub unless used_trade_hubs.include?( trade_hub )
      end
    end
    [used_item, used_trade_hubs]
  end

  def get_occuped_places
    if remove_occuped_places
      if( key_user_id && api_key )
        EAAL.cache = EAAL::Cache::FileCache.new( 'tmp' )
        api = EAAL::API.new( key_user_id, api_key )
        api.scope = "account"
        characters = api.Characters
        characters_ids = characters.characters.map{ |e| e.characterID }
        full_orders_list = []
        api.scope = "char"
        characters_ids.each do |char_id|
          full_orders_list << api.MarketOrders(:characterID => char_id).orders.reject{ |e| e.orderState != '0' }
        end
        full_orders_list.flatten!
        small_orders_list = full_orders_list.map{ |o| [o.stationID.to_i,o.typeID.to_i] }
        return small_orders_list
      end
    end
    [] # if case not checked return an empty array
  end

end
