class ProductionCostsController < ApplicationController

  before_action :set_user, :set_small_screen, :set_show_update_daily

  caches_page :show, :dailies_avg_prices

  def show
    @title = 'Production cost estimation'
    @item = EveItem.find_by( id: params[ :id ] )
    raise 'Base item cost should call dailies_avg_price instead of show' if @item.base_item
  end

  # We put this here to ease the cache management
  def dailies_avg_prices
    @item = EveItem.find_by( id: params[ :item_id ] )
    @title = @item.base_item ? 'Sales details included in price computation ' : 'Weekly price detail'
    @dailies_details = @item.weekly_price_details.where(trade_hub_id: params[:trade_hub_id]).order( 'day DESC' ).paginate( :page => params[:page] )
  end

end
