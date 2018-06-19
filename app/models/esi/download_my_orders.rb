require_relative 'download'

class Esi::DownloadMyOrders < Esi::Download

  def initialize( debug_request: false )
    super( nil, {}, debug_request: debug_request )
  end

  def update
    Banner.p 'About to download users orders.'
    User.where.not( last_used_character_id: nil ).each do |user|
      update_user user
    end
  end

  private

  def update_user( user )

    character = user.last_used_character
    character_id = character.eve_id
    @rest_url = "characters/#{character_id}/orders/"

    set_auth_token

    pages = get_all_pages

    current_trade_orders_id = TradeOrder.pluck( :id )

    ActiveRecord::Base.transaction do

      pages.each do |page|
        eve_item_id = EveItem.to_eve_item_id(page['type_id'])
        trade_hub_id =  Station.to_trade_hub_id(page['location_id'])

        to = TradeOrder.where( user: character.user, eve_item_id: eve_item_id, trade_hub_id: trade_hub_id ).first_or_initialize
        to.price = page['price']
        to.save!

        current_trade_orders_id.delete( to.id )
      end

      character.user.trade_orders.where( id: current_trade_orders_id ).delete_all

    end
  end

end