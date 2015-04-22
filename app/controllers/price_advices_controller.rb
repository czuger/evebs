require 'time_diff'

class PriceAdvicesController < ApplicationController
  def show
    @user = current_user
    @prices_array = []
    @no_concurent_array = []
    # This mean we already have an order for that item on that hub
    # TODO : add a catch there to check for eve api connection errors
    @fullfilled_orders = @user.get_occuped_places
    @item_count = {}

    @print_change_warning=print_change_warning

    @user.eve_items.each do |eve_item|
      @user.trade_hubs.each do |trade_hub|
        next if @fullfilled_orders.include?([trade_hub.id,eve_item.id])

        min_price_item = MinPrice.where( 'eve_item_id = ? AND trade_hub_id = ?', eve_item.id, trade_hub.id ).first
        if min_price_item

          @item_count[eve_item.name]+=1 if @item_count.has_key?( eve_item.name )
          @item_count[eve_item.name]=1 unless @item_count.has_key?( eve_item.name )

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

  private
  def print_change_warning
    lcic = @user.last_changes_in_choices || Time.new(0)
    last_check = Time.now.beginning_of_hour
    if lcic > last_check
      diff = Time.diff( Time.now, Time.now.end_of_hour, '%N %S' )[:diff]
      return "Your changes will be computed in #{diff}"
    end
    nil
  end
end

