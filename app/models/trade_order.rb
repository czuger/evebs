class TradeOrder < ActiveRecord::Base
  belongs_to :user
  belongs_to :eve_item
  belongs_to :trade_hub

  validates :user_id, :eve_item_id, :trade_hub_id, :new_order, presence: true

  # TODO : create the rake task
  # TODO : (for each users)

  def self.get_trade_orders(user)
    if user.remove_occuped_places
      if( user.key_user_id && !user.key_user_id.empty? && user.api_key && !user.api_key.empty? )
        EAAL.cache = EAAL::Cache::FileCache.new( 'tmp' )
        api = EAAL::API.new( user.key_user_id, user.api_key )
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
        # TradeOrder.update_all( new_order: false )
        user.trade_orders.each do |trade_order|
          trade_order.update_attributes( { new_order: false } )
        end
        full_orders_list.each do |order|
          eve_item_id = EveItem.to_eve_item_id(order.typeID.to_i)
          trade_hub_id =  Station.to_trade_hub_id(order.stationID.to_i)
          to = TradeOrder.find_by_user_id_and_eve_item_id_and_trade_hub_id(user.id, eve_item_id, trade_hub_id)
          if to
            # Si l'ordre existe déja on le renouvelle
            to.update_attributes( { new_order: true } )
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
