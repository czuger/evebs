class MarketDataController < ApplicationController

  before_action :set_user, :set_small_screen, :set_show_update_hourly
  caches_page :market_overview, :trade_hub_detail

	MARKET_OVERVIEW_TITLE = 'Trade hubs prices comparison for '

  def market_overview
    @item = EveItem.find( params[ :item_id ] )

    # set_checked_production_list_ids

    @title = MARKET_OVERVIEW_TITLE + view_context.link_to( @item.name, item_path( @item ) )
    @meta_title = MARKET_OVERVIEW_TITLE + @item.name

    @meta_content = 'Compare prices for ' + @item.name + ' in  all trade hubs. ' +
			'Compare an estimation of the expected margin, the min price, and average margin, an average price and the monthly volume.'

    if @item.base_item
      @item_prices = @item.prices_mins.includes( {trade_hub: :region} ).order( 'min_price NULLS LAST' )
    else
      @item_prices = @item.price_advices_min_prices.order( 'vol_month DESC NULLS LAST, margin_percent DESC NULLS LAST' )
    end
  end

  def trade_hub_detail
    @trade_hub = TradeHub.find( params[ :trade_hub_id ] )
    @element = EveItem.find( params[ :item_id ] )

    @title = view_context.link_to( @element.name, item_path( @element ) ) + ' current sell orders at ' + @trade_hub.name

    @meta_title = @element.name + ' current sell orders at ' + @trade_hub.name
    @meta_content = 'Show current sell orders for ' + @element.name + ' in the trade hub Jita.'

    @orders = PublicTradeOrder.where( trade_hub_id: params[ :trade_hub_id ], eve_item_id: params[ :item_id ], is_buy_order: false )
                  .order( 'price' ).limit( 20 )
  end

end
