class UserSaleOrdersController < ApplicationController

  before_action :require_logged_in!, :log_client_activity
  before_action :set_user

  def show
    @user = current_user
    @print_change_warning=print_change_warning

    @trade_hubs_names = @user.user_sale_order_details.distinct.order( :trade_hub_name ).pluck( :trade_hub_name, :trade_hub_id )
    @item_names = @user.user_sale_order_details.distinct.order( :eve_item_name ).pluck( :eve_item_name, :eve_item_id )

    @compared_prices = @user.user_sale_order_details.order( :trade_hub_name, :eve_item_name )

    lod = @user.last_orders_download ? @user.last_orders_download : Time.at( 0 )
    @data_available_in = (lod + UserSaleOrder::CACHE_DURATION - Time.now).round
  end

  def update
    @user.update( download_orders_running: true )
    DownloadMyOrdersJob.perform_later( @user )
    redirect_to user_sale_orders_path
  end

  private

  def print_change_warning
    lcic = @user.last_changes_in_choices || Time.new(0)
    last_check = Time.now.beginning_of_hour
    if lcic > last_check
      diff = Time.diff( Time.now, Time.now.end_of_hour, '%N %S' )[:diff]
      return "You did recent changes. Some datas can be inacurate. The next data refresh will occur in : #{diff}"
    end
    nil
  end

end