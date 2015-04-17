class PriceAdvicesController < ApplicationController
  def show
    @user = User.first
    @prices_array = []
    @no_concurent_array = []
    @user.eve_items.each do |eve_item|
      @user.trade_hubs.each do |trade_hub|
        min_price_item = MinPrice.where( 'eve_item_id = ? AND trade_hub_id = ?', eve_item.id, trade_hub.id ).first
        if min_price_item
          @prices_array << {
            trade_hub: trade_hub.name,
            eve_item: eve_item.name,
            benef: min_price_item ? min_price_item.min_price - eve_item.cost : 'Not sold there'
          }
        else
          @no_concurent_array << {
            trade_hub: trade_hub.name,
            eve_item: eve_item.name
          }
        end
      end
    end
    @prices_array.sort_by!{ |h| h[:benef] }
    @prices_array.reverse!
  end
end
