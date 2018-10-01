class ProductionCostsController < ApplicationController

  before_action :set_user
  caches_page :show

  def show
    @item = EveItem.find_by( id: params[ :id ] )

    if @item.base_item
      @dailies_datails = @item.weekly_price_details.order( 'day DESC' ).paginate( :page => params[:page] )
    end
  end

end
