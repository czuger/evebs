require_relative 'download'

class Esi::DownloadMyOrders < Esi::Download

  def initialize( debug_request: false )
    super( nil, {}, debug_request: debug_request )
  end

  def update( user )

    if user.locked
      puts "#{user.name} is locked. Skipping ..."
      return
    end

    user_id = user.uid
    @rest_url = "characters/#{user_id}/orders/"

    return unless set_auth_token( user )

    pages = get_all_pages

    unless pages
      user.update( locked: true )
      return
    end

    current_trade_orders_id = UserSaleOrder.pluck(:id )

    ActiveRecord::Base.transaction do

      pages.each do |page|
        eve_item_id = EveItem.to_eve_item_id(page['type_id'])
        trade_hub_id =  Station.to_trade_hub_id(page['location_id'])

        # We can set orders in other hubs than those we have in the database.
        next unless trade_hub_id

        to = UserSaleOrder.where(user: user, eve_item_id: eve_item_id, trade_hub_id: trade_hub_id ).first_or_initialize
        to.price = page['price']
        to.save!

        current_trade_orders_id.delete( to.id )

        if user.remove_occuped_places
          ProductionList.where(user_id: user.id, eve_item_id: eve_item_id, trade_hub_id: trade_hub_id ).delete_all
        end
      end

      user.user_sale_orders.where( id: current_trade_orders_id ).delete_all

      user.update( download_orders_running: false, last_orders_download: Time.now )

    end
  end

end