class BuyOrdersController < ApplicationController

  before_action :require_logged_in!, :log_client_activity
  before_action :set_user, :set_wide_screen, :set_show_update_hourly

  include Modules::CheckedProductionListIds

  def show
    @title = 'Show rentability with buy orders'
    set_checked_production_list_ids
    @buy_orders = @user.buy_orders_analytics_results.paginate(:page => params[:page], :per_page => 20 )
  end

end
