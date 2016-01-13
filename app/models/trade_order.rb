require_relative 'trade_orders/get_full_order_list'

require 'pp'

class TradeOrder < ActiveRecord::Base
  belongs_to :user
  belongs_to :eve_item
  belongs_to :trade_hub

  validates :user_id, :eve_item_id, :trade_hub_id, :new_order, presence: true

  include GetFullOrderList

  # TODO : create the rake task
  # TODO : (for each users)

  def self.get_trade_orders(user)
    if user.remove_occuped_places || user.watch_my_prices
      puts "About to retrieveing orders for #{user.name}"
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
          get_full_order_list( full_orders_list )
          # On supprime tous les ordres marqués comme anciens
          TradeOrder.destroy_all( new_order: false )
        rescue StandardError => exception
          STDERR.puts '#'*50
          STDERR.puts Time.now
          STDERR.puts "In #{self.class}##{__method__} for #{user.name}-#{user.id}"
          STDERR.puts exception.message
          STDERR.puts '#'*50
         # STDERR.puts exception.backtrace
        rescue EAAL::Exception => exception
          STDERR.puts '#'*50
          STDERR.puts Time.now
          STDERR.puts "In #{self.class}##{__method__} for #{user.name}-#{user.id}"
          STDERR.puts exception.message
          STDERR.puts exception.backtrace
          STDERR.puts '#'*50
        end
      end
    else
      puts "#{user.name} didn't ask for sales orders check"
    end
  end

end
