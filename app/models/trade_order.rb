class TradeOrder < ActiveRecord::Base
  belongs_to :user
  belongs_to :eve_item
  belongs_to :trade_hub

  validates :user_id, :eve_item_id, :trade_hub_id, :new_order, presence: true

  # TODO : create the rake task
  # TODO : (for each users)

  def self.get_occuped_places(user)
    if user.remove_occuped_places
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
        # On considère tous les ordres actuels comme des anciens ordres
        TradeOrder.update_all( new_order: false )
        full_orders_list.each do |order|
          eve_item_id = EveItem.to_eve_item_id(o.typeID.to_i)
          trade_hub_id =  Station.to_trade_hub_id(o.stationID.to_i)
          to = TradeOrder.find_by_user_id_and_eve_item_id_and_trade_hub_id(user.id, eve_item_id, trade_hub_id)
          if to
            # Si l'ordre existe déja on le renouvelle
            to.update_attribute( new_order: true )
          else
            # Sinon on en cree un
            TradeOrder.create!( user: user, eve_item_id: eve_item_id, trade_hub_id: trade_hub_id, new_order: true )
          end
        end
        # On supprime tous les ordres marqués comme anciens
        TradeOrder.delete_all( new_order: false )
      end
    end
  end

end
