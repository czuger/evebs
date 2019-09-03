class ProductionCostsController < ApplicationController

  before_action :set_user, :set_small_screen, :set_show_update_daily

  caches_page :show, :dailies_avg_prices

  def show
    set_no_title_header

    @item = EveItem.find_by( id: params[ :id ] )

    @meta_title = 'Production cost estimation for ' + @item.name
    @meta_content = 'This page show detailed cost estimation for ' + @item.name

    raise 'Base item cost should call dailies_avg_price instead of show' if @item.base_item
  end

  # We put this here to ease the cache management
  def dailies_avg_prices
    @item = EveItem.find_by( id: params[ :item_id ] )
    @title = @item.base_item ? 'Sales details included in price computation ' : 'Weekly price detail'
    @dailies_details = @item.weekly_price_details.where(trade_hub_id: params[:trade_hub_id]).order( 'day DESC' ).paginate( :page => params[:page] )
  end

  def market_histories
		set_no_title_header

    @item = EveItem.find_by( id: params[ :production_cost_id ] )

    @meta_title = 'Regional information about ' + @item.name
		@meta_content = 'This page shows compiled information about ' + @item.name +
			' in all regions of New Eden. Information are : total volume, average price, max price and min price.'

    @market_histories = @item.group_eve_market_histories.order('volume DESC')
  end


end
