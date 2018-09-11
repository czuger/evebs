class BuyOrdersController < ApplicationController

  before_action :require_logged_in!, :log_client_activity
  before_action :set_user

  include Modules::CheckedProductionListIds

  def show
    set_checked_production_list_ids
    @buy_orders = @user.buy_orders_analytics_results.paginate(:page => params[:page], :per_page => 20 )
  end

end
