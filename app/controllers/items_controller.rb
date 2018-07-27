class ItemsController < ApplicationController

  before_action :require_logged_in!, :log_client_activity
  before_action :set_user

  include Modules::Nvl
  include Modules::CheckedProductionListIds

  def index
    @user = current_user
    @item_ids = @user.eve_item_ids.uniq
  end

  def cost
    @item = EveItem.includes( :blueprint ).find_by( id: params[ :item_id ] )
  end

  def show
    @item = EveItem.find( params[ :id ] )

    set_checked_production_list_ids

    if @item.prices_advices.exists?
      @item_prices = @item.prices_advices.includes( { trade_hub: :region } ).order( 'vol_month DESC NULLS LAST, min_price DESC NULLS LAST' )
    else
      @min_prices = @item.prices_mins.includes( { trade_hub: :region } ).order( 'min_price ASC NULLS LAST' )
    end
  end

  def trade_hub_detail
    @trade_hub = TradeHub.find( params[ :trade_hub_id ] )
    @element = EveItem.find( params[ :item_id ] )
    @orders = SalesOrder.where( trade_hub_id: params[ :trade_hub_id ], eve_item_id: params[ :item_id ] )
                  .order( 'price' ).limit( 20 )
  end

end
