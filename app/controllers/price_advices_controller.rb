require 'time_diff'

class PriceAdvicesController < ApplicationController

  before_action :require_logged_in!

  include PriceAdvicesMarginModule
  include ShoppingBasketsModule

  def advice_prices_monthly
    advice_prices_margins( :monthly )
  end

  def advice_prices
    advice_prices_margins( :daily )
  end

  def show_challenged_prices

    @user = current_user
    @print_change_warning=print_change_warning

    @trade_orders = @user.trade_orders.includes( { eve_item: :blueprint }, :trade_hub )
    @compared_prices = []

    @trade_orders.each do |to|
      min_price = MinPrice.find_by_eve_item_id_and_trade_hub_id( to.eve_item_id, to.trade_hub_id )

      min_price = min_price.min_price if min_price

      prod_qtt = to.eve_item.blueprint.prod_qtt
      cost = to.eve_item.cost / prod_qtt
      margin_pcent = ( min_price / cost ) - 1 if cost && min_price

      @compared_prices << {
          trade_hub_name: to.trade_hub.name, eve_item_name: to.eve_item.name, my_price: to.price,
          min_price: min_price, cost: cost, margin_pcent: margin_pcent, eve_item_id: to.eve_item_id,
          eve_item_cpp_id: to.eve_item.cpp_eve_item_id, trade_hub_cpp_id: to.trade_hub.eve_system_id
      }

      set_trade_hubs( to.trade_hub.name )
      set_items( to.eve_item.name )

    end

    @compared_prices = @compared_prices.sort_by{ |e| [e[:trade_hub_name], e[:eve_item_name]] }

  end

  def show_item_detail
    @item = EveItem.find( params[ :item_id ] )

    current_min_price_hash = {}
    current_min_prices = MinPrice.where( eve_item_id: @item.id )
    current_min_price_hash = Hash[ current_min_prices.map{ |e| [ e.trade_hub_id, e.min_price ] } ] if current_min_prices

    avg_prices_hash = {}
    last_month_averages = CrestPricesLastMonthAverage.where( eve_item_id: @item.id )
    if last_month_averages
      last_month_averages.each do |last_month_average|
        last_month_average.region.trade_hub_ids.each do |trade_hub_id|
          avg_prices_hash[trade_hub_id] = last_month_average
        end
      end
    end

    @item_cost = @item.single_unit_cost
    trade_hubs_ids = (current_min_price_hash.keys + avg_prices_hash.keys).uniq
    @final_array = []
    TradeHub.where( id: trade_hubs_ids ).order( :name ).each do |trade_hub|
      avg_price = avg_prices_hash[trade_hub.id].avg_price_avg if avg_prices_hash[trade_hub.id]
      @final_array << {
        trade_hub: trade_hub.name,
        cost: @item_cost,
        min_price_margin: @item.pcent_margin( current_min_price_hash[trade_hub.id] ),
        min_price: current_min_price_hash[trade_hub.id],
        avg_price_margin: @item.pcent_margin( avg_price ),
        avg_price: avg_price,
        volume: (avg_prices_hash[trade_hub.id].volume_sum if avg_prices_hash[trade_hub.id])
      }
    end

    @final_array.sort_by!{ |e| nvl( e[:volume] ) }
    @final_array.reverse!

  end

  def update_basket
    user_id, trade_hub_id, eve_item_id = params[:item_code].split('|')
    checked = params[:checked] == 'true'

    if checked
      unless ShoppingBasket.find_by_user_id_and_trade_hub_id_and_eve_item_id( user_id, trade_hub_id, eve_item_id )
        ShoppingBasket.create!( user_id: user_id, trade_hub_id: trade_hub_id, eve_item_id: eve_item_id )
      end
    else
      sb = ShoppingBasket.delete_all( user_id: user_id, trade_hub_id: trade_hub_id, eve_item_id: eve_item_id )
    end
    render nothing: true
  end

  private

  def print_change_warning
    lcic = @user.last_changes_in_choices || Time.new(0)
    last_check = Time.now.beginning_of_hour
    if lcic > last_check
      diff = Time.diff( Time.now, Time.now.end_of_hour, '%N %S' )[:diff]
      return "You did recent changes. Some datas can be inacurate. The next data refresh will occur in : #{diff}"
    end
    nil
  end

  def get_montly_items_averages
    datas = CrestPricesLastMonthAverage.where( eve_item_id: @user.eve_items, region_id: @user.regions.pluck(:id) ).to_a
    Hash[datas.map{ |e| [[[e.region_id],[e.eve_item_id]],e]}]
  end

  def set_trade_hubs( trade_hub_name )
    @trade_hubs_names = [] unless @trade_hubs_names
    @trade_hubs_names << trade_hub_name unless @trade_hubs_names.include?( trade_hub_name )
    @trade_hubs_names.sort!
  end

  def set_items( item_name )
    @item_names = [] unless @item_names
    @item_names << item_name unless @item_names.include?( item_name )
    @item_names.sort!
  end

  # If a number does not exist : then assigns it to minus infinity
  def nvl( number )
    number ? number : -Float::INFINITY
  end
end

