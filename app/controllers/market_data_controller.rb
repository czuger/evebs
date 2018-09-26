class MarketDataController < ApplicationController

  before_action :set_user
  caches_page :market_overview, :trade_hub_detail

  def market_overview
    @item = EveItem.find( params[ :item_id ] )

    # set_checked_production_list_ids

    if @item.base_item
      @item_prices = @item.prices_mins.includes( {trade_hub: :region} ).order( 'min_price NULLS LAST' )
    else
      @item_prices = @item.price_advices_min_prices.order( 'vol_month DESC NULLS LAST, margin_percent DESC NULLS LAST' )
    end
  end

  def trade_hub_detail
    @trade_hub = TradeHub.find( params[ :trade_hub_id ] )
    @element = EveItem.find( params[ :item_id ] )
    @orders = PublicTradeOrder.where( trade_hub_id: params[ :trade_hub_id ], eve_item_id: params[ :item_id ], is_buy_order: false )
                  .order( 'price' ).limit( 20 )
  end


end
