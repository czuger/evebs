class ProductionCostsController < ApplicationController

  before_action :set_user, :set_small_screen, :set_show_update_daily

  caches_page :show, :dailies_avg_prices

	DAILIES_AVG_PRICES_TITLE = 'Weekly average price detail for '
	PRODUCTION_COST_TITLE = 'Production cost estimation for '

  def show
    @item = EveItem.find_by( id: params[ :id ] )

		raise "Should not be called only for base item : #{@item.inspect}" if @item.base_item

		@title = DAILIES_AVG_PRICES_TITLE + view_context.link_to( @item.name, item_path( @item ) )
		@meta_title = PRODUCTION_COST_TITLE + @item.name
    @meta_content = 'This page show detailed cost estimation for ' + @item.name

		@breadcrumb = Misc::BreadcrumbElement.bc_from_sub_item( 'Production cost',
																														view_context.production_cost_url( @item ),
																														@item, view_context )
  end

  # We put this here to ease the cache management
  def dailies_avg_prices
    @item = EveItem.find_by( id: params[ :item_id ] )

		raise "Should be called only for base item : #{@item.inspect}" unless @item.base_item

		@title = DAILIES_AVG_PRICES_TITLE + view_context.link_to( @item.name, item_path( @item ) ) + ' ' + view_context.print_total_cost_for_items( @item )
		@meta_title = DAILIES_AVG_PRICES_TITLE + @item.name

		@meta_content = 'The price of a basic item is computed over a weekly average of the price each day.'

    @dailies_details = @item.weekly_price_details.where(trade_hub_id: params[:trade_hub_id]).order( 'day DESC' ).paginate( :page => params[:page] )
  end

  def market_histories
		set_no_title_header

    @item = EveItem.find_by( id: params[ :production_cost_id ] )

    @meta_title = 'Regional information about ' + @item.name
		@meta_content = 'This page shows compiled information about ' + @item.name +
			' in all regions of New Eden. Information are : total volume, average price, max price and min price.'

    @market_histories = @item.group_eve_market_histories.order('volume DESC')

		@breadcrumb = Misc::BreadcrumbElement.bc_from_sub_item( 'Last month aggregations',
																														production_cost_market_histories_url( @item ),
																														@item, view_context )

  end


end
