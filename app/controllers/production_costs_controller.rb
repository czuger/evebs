class ProductionCostsController < ApplicationController

  before_action :set_user
  caches_page :show, :dailies_avg_prices

  def show
    @item = EveItem.find_by( id: params[ :id ] )
    raise 'Base item cost should call dailies_avg_price instead of show' if @item.base_item
  end

  # We put this here to ease the cache management
  def dailies_avg_prices
    @item = EveItem.find_by( id: params[ :item_id ] )
    @dailies_details = @item.weekly_price_details.order( 'day DESC' ).paginate( :page => params[:page] )
  end

end
