require 'pp'

class TradeOrder < ActiveRecord::Base
  belongs_to :user
  belongs_to :eve_item
  belongs_to :trade_hub

  validates :user_id, :eve_item_id, :trade_hub_id, :new_order, presence: true

  # TODO : create the rake task
  # TODO : (for each users)

  def self.get_trade_orders(user)
    if user.remove_occuped_places || user.watch_my_prices
      if( user.key_user_id && !user.key_user_id.empty? && user.api_key && !user.api_key.empty? )
        EAAL.cache = EAAL::Cache::FileCache.new( 'tmp' )
        api = EAAL::API.new( user.key_user_id, user.api_key )
        api.scope = "account"
        begin
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
            puts "Setting #{trade_order.inspect} - new_order to false"
            trade_order.update_attribute( :new_order, false )
          end
          full_orders_list.each do |order|
            puts "Order received #{order.typeID}, #{order.stationID}, #{order.price}"
            eve_item_id = EveItem.to_eve_item_id(order.typeID.to_i)
            trade_hub_id =  Station.to_trade_hub_id(order.stationID.to_i)
            if trade_hub_id && eve_item_id
              to = TradeOrder.find_by_user_id_and_eve_item_id_and_trade_hub_id(user.id, eve_item_id, trade_hub_id)
              if to
                # Si l'ordre existe déja on le renouvelle
                puts "Found #{to.inspect}, updating"
                to.update_attributes( { new_order: true, price: order.price } )
              else
                # Sinon on en cree un
                puts "Order not found - creating a new one"
                TradeOrder.create!( user: user, eve_item_id: eve_item_id, trade_hub_id: trade_hub_id, new_order: true, price: order.price )
              end
            else
              STDERR.puts "#{Time.now} - TradeOrder.get_trade_orders - Unable to find eve item for id #{order.typeID}" unless eve_item_id
              STDERR.puts "#{Time.now} - TradeOrder.get_trade_orders - Unable to find trade hub for station #{order.stationID}" unless trade_hub_id
            end
          end
          # On supprime tous les ordres marqués comme anciens
          TradeOrder.destroy_all( new_order: false )
        rescue EAAL::Exception::HTTPError => exception
          STDERR.puts Time.now
          STDERR.puts user.inspect
          STDERR.puts exception.message
          STDERR.puts exception.backtrace
        rescue => exception
         STDERR.puts Time.now
         STDERR.puts exception.message
         STDERR.puts exception.backtrace
        end
      end
    end
  end

end
