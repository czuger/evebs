class PriceAdvicesController < ApplicationController
  def show
    @user = User.first
    @prices_array = []
    @no_concurent_array = []
    @user.eve_items.each do |eve_item|
      @user.trade_hubs.each do |trade_hub|
        min_price_item = MinPrice.where( 'eve_item_id = ? AND trade_hub_id = ?', eve_item.id, trade_hub.id ).first
        if min_price_item
          blueprint = eve_item.blueprint
          batch_size = blueprint.nb_runs*blueprint.prod_qtt
          batch_cost = eve_item.cost*blueprint.nb_runs
          batch_sell_price = min_price_item.min_price*batch_size
          benef = batch_sell_price - batch_cost
          benef_pcent = ((batch_sell_price*100) / batch_cost).round(0)-100
          @prices_array << {
            trade_hub: trade_hub.name,
            eve_item: eve_item.name,
            min_price: min_price_item.min_price.round(1),
            cost: (eve_item.cost/blueprint.prod_qtt).round(1),
            benef: benef,
            benef_pcent: benef_pcent
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
