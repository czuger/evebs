class ProductionCostsController < ApplicationController

  before_action :set_user, :set_small_screen, :set_show_update_daily

  caches_page :show, :dailies_avg_prices

	DAILIES_AVG_PRICES_TITLE = 'Weekly average price detail for '
	PRODUCTION_COST_TITLE = 'Production cost estimation for '
	MARKET_HISTORIES_TITLE = 'Regional information about '

  def show
    @item = EveItem.friendly.find( params[ :id ] )

		raise "Should not be called only for base item : #{@item.inspect}" if @item.base_item

		@title = PRODUCTION_COST_TITLE + view_context.link_to( @item.name, item_path( @item ) )
		@meta_title = PRODUCTION_COST_TITLE + @item.name
    @meta_content = 'This page show detailed cost estimation for ' + @item.name

		@breadcrumb = Misc::BreadcrumbElement.bc_from_sub_item( 'Production cost',
																														view_context.production_cost_url( @item ),
																														@item, view_context )

		@taxes = Constant.find_by_libe( 'taxes' )
    raise 'Taxes not set, please set them using the console.' unless @taxes
    # Set the taxes using something like
    # Constant.create!( libe: 'taxes', f_value: 1.13, description: 'This include the production taxes (5% est.), the broker fees (4% est.), and the sales taxes
    @taxes = @taxes.f_value
  end

  # We put this here to ease the cache management
  def dailies_avg_prices
    @item = EveItem.friendly.find( params[ :item_id ] )

		raise "Should be called only for base item : #{@item.inspect}" unless @item.base_item

		@title = DAILIES_AVG_PRICES_TITLE + view_context.link_to( @item.name, item_path( @item ) ) + ' ' + view_context.print_total_cost_for_items( @item )
		@meta_title = DAILIES_AVG_PRICES_TITLE + @item.name

		@meta_content = 'The price of a basic item is computed over a weekly average of the price each day.'

    @dailies_details = @item.weekly_price_details.where(trade_hub_id: params[:trade_hub_id]).order( 'day DESC' ).paginate( :page => params[:page] )
  end

  def market_histories
		@item = EveItem.friendly.find( params[ :production_cost_id ] )

		@title = MARKET_HISTORIES_TITLE + view_context.link_to( @item.name, item_path( @item ) )

    @meta_title = 'Regional information about ' + @item.name
		@meta_content = 'This page shows compiled information about ' + @item.name +
			' in all regions of New Eden. Information are : total volume, average price, max price and min price.'

    @market_histories = @item.eve_market_histories_groups.joins( :universe_region ).order('volume DESC')
			.select( 'universe_regions.name AS region_name', :volume, :highest, :lowest, :average )

		unless @item.base_item
			@breadcrumb = Misc::BreadcrumbElement.bc_from_sub_item( 'Last month aggregations',
																															production_cost_market_histories_url( @item ),
																															@item, view_context )
		end
  end

end
