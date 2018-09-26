class ProductionCostsController < ApplicationController

  before_action :set_user
  caches_page :show

  def show
    @item = EveItem.find_by( id: params[ :id ] )

    if @item.base_item
      jita = get_jita
      @sales_final_detail = SalesFinal.where( eve_item_id: @item.id, trade_hub_id: jita.id ).
          where( 'day >= ( current_date - 7 )' ).order( 'day DESC, created_at DESC' ).
          paginate( :page => params[:page] )
    end
  end

end
