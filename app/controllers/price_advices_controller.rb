require 'time_diff'

class PriceAdvicesController < ApplicationController

  before_action :require_logged_in!, :log_client_activity

  include Modules::PriceAdvices::MarginModule
  include Modules::PriceAdvices::ShoppingBasketsModule
  include Modules::PriceAdvices::ShowChallengedPrices
  include Modules::Nvl

  def advice_prices_monthly
    advice_prices_margins( :monthly )
  end

  def advice_prices
    advice_prices_margins( :daily )
  end

  def empty_places
    # Attention : min price, veut dire : last sold min price, pas last current min price.
    @user = current_user
    @empty_places_objects = PricesAdvice.joins( :eve_item, :region, :trade_hub ).where( eve_item: @user.eve_items, trade_hub: @user.trade_hubs )
      .where( min_price: nil ).where.not( vol_month: nil )
      .where.not( SalesOrder.where( closed: false )
         .where( 'prices_advices.eve_item_id = sales_orders.eve_item_id AND prices_advices.trade_hub_id = sales_orders.trade_hub_id' )
            .exists )
      .order( 'vol_month DESC' ).paginate(:page => params[:page], :per_page => 20 )

    @empty_places_array = @empty_places_objects
      .pluck_to_hash( 'trade_hubs.name', 'regions.name', 'eve_items.name', 'eve_items.id', :vol_month, :avg_price, :single_unit_cost )
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

end

