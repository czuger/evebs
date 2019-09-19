class BuyOrdersController < ApplicationController

  before_action :require_logged_in!, :log_client_activity
  before_action :set_user, :set_show_update_hourly

  include Modules::CheckedProductionListIds

  def show
    @title = 'Show rentability with buy orders'
    set_checked_production_list_ids

		if @user.batch_cap
			@buy_orders = @user.buy_orders_analytics_results.where( 'capped_margin > 0' ).order( 'capped_margin DESC')
		else
			@buy_orders = @user.buy_orders_analytics_results.where( 'full_margin > 0' ).order( 'full_margin DESC')
		end

		@buy_orders = @buy_orders.paginate(:page => params[:page], :per_page => 12 )
  end

end
