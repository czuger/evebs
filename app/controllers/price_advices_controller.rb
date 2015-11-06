require 'time_diff'

class PriceAdvicesController < ApplicationController

  before_action :require_logged_in!

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

end

