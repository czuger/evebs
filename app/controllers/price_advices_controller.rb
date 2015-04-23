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

    @user.trade_hubs.each do |trade_hub|
      eve_items_ids = @user.eve_item_ids
      eve_items_ids.reject!{ |i| @fullfilled_orders.include?([trade_hub.id,i]) }

      min_price_items = MinPrice.includes(eve_item:[:blueprint]).where( { eve_item_id: eve_items_ids, trade_hub_id: trade_hub.id } )
      min_price_items.each do |min_price_item|

        @item_count[min_price_item.eve_item.name]+=1 if @item_count.has_key?( min_price_item.eve_item.name )
        @item_count[min_price_item.eve_item.name]=1 unless @item_count.has_key?( min_price_item.eve_item.name )

        blueprint = min_price_item.eve_item.blueprint
        batch_size = blueprint.nb_runs*blueprint.prod_qtt
        batch_cost = min_price_item.eve_item.cost*blueprint.nb_runs
        batch_sell_price = min_price_item.min_price*batch_size
        benef = batch_sell_price - batch_cost
        benef_pcent = ((batch_sell_price*100) / batch_cost).round(0)-100
        if benef_pcent > @user.min_pcent_for_advice
          @prices_array << {
            trade_hub: trade_hub.name,
            eve_item: min_price_item.eve_item.name,
            min_price: min_price_item.min_price.round(1),
            cost: (min_price_item.eve_item.cost/blueprint.prod_qtt).round(1),
            benef: benef,
            benef_pcent: benef_pcent,
            batch_size: batch_size
          }
        end
      end
    end

    # TODO : need to fix the no concurent issue
      #   else
      #     @no_concurent_array << {
      #       trade_hub: trade_hub.name,
      #       eve_item: min_price_item.eve_item.name
      #     }
      #   end
      # end
    # end

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

