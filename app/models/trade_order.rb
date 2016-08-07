require_relative 'trade_orders/get_full_order_list'

require 'pp'

class TradeOrder < ActiveRecord::Base
  belongs_to :user
  belongs_to :eve_item
  belongs_to :trade_hub

  validates :user_id, :eve_item_id, :trade_hub_id, :new_order, presence: true

  extend TradeOrders::GetFullOrderList

  # TODO : create the rake task
  # TODO : (for each users)

  def self.get_trade_orders(user)
    if user.remove_occuped_places || user.watch_my_prices
      puts "About to retrieveing orders for #{user.name}" unless Rails.env == 'test'
      if( user.key_user_id && !user.key_user_id.empty? && user.api_key && !user.api_key.empty? )
        # EAAL.cache = EAAL::Cache::FileCache.new( 'tmp' )
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
            puts "Setting #{trade_order.inspect} - new_order to false" unless Rails.env == 'test'
            trade_order.update_attribute( :new_order, false )
          end
          get_full_order_list( user, full_orders_list )
          # On supprime tous les ordres marqués comme anciens
          TradeOrder.destroy_all( new_order: false )

        rescue StandardError => exception

          STDERR.puts '#'*50

          if exception.class.to_s =~ /EveAPIException/
            STDERR.puts 'EveAPIException'

            user.api_key_errors.create!( error_message: exception.inspect, user_message: exception.message )
            user.update_attributes( remove_occuped_places: false, watch_my_prices: false )
            puts 'Algo will stop checking orders for this user'
            puts

          else
            STDERR.puts StandardError
            standard_error = true
          end

          STDERR.puts Time.now
          STDERR.puts "In TradeOrder##{__method__} for #{user.name}-#{user.id}"
          STDERR.puts exception.message

          # STDERR.puts exception.inspect
          STDERR.puts exception.backtrace if standard_error
          STDERR.puts '#'*50

        end
      end
    else
      puts "#{user.name} didn't ask for sales orders check" unless Rails.env == 'test'
    end
  end

end
