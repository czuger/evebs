require_relative 'download'

class Esi::DownloadMyOrders < Esi::Download

  def initialize( debug_request: false )
    super( nil, {}, debug_request: debug_request )
  end

  def update
    Banner.p 'About to download users orders'
    User.where.not( last_used_character_id: nil ).where( watch_my_prices: true ).each do |user|
      download_orders user
    end
  end

  private

  def download_orders( user )

    character = user.last_used_character

    if character.locked
      puts "#{character.name} is locked. Skipping ..."
      return
    end

    character_id = character.eve_id
    @rest_url = "characters/#{character_id}/orders/"

    set_auth_token

    pages = get_all_pages

    unless pages
      character.update( locked: true )
      return
    end

    current_trade_orders_id = TradeOrder.pluck( :id )

    ActiveRecord::Base.transaction do

      pages.each do |page|
        eve_item_id = EveItem.to_eve_item_id(page['type_id'])
        trade_hub_id =  Station.to_trade_hub_id(page['location_id'])

        # We can set orders in other hubs than those we have in the database.
        next unless trade_hub_id

        to = TradeOrder.where( user: character.user, eve_item_id: eve_item_id, trade_hub_id: trade_hub_id ).first_or_initialize
        to.price = page['price']
        to.save!

        current_trade_orders_id.delete( to.id )

        if user.remove_occuped_places
          ShoppingBasket.where( user_id: character.user_id, eve_item_id: eve_item_id, trade_hub_id: trade_hub_id ).delete_all
        end
      end

      character.user.trade_orders.where( id: current_trade_orders_id ).delete_all

    end
  end

end