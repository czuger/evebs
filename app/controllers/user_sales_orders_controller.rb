class UserSalesOrdersController < ApplicationController

  before_action :require_logged_in!, :log_client_activity
  before_action :set_user

  def show
    @user = current_user
    @print_change_warning=print_change_warning

    @selected_trade_hub_id = params['trade_hub_id']
    @selected_eve_item_id = params['eve_item_id']

    filtered_users_sales_order_details = @user.user_sale_order_details

    if @user.sales_orders_show_margin_min
      filtered_users_sales_order_details = filtered_users_sales_order_details.where( 'min_price_margin_pcent > ?', @user.sales_orders_show_margin_min * 0.01 )
    end

    @trade_hubs_names = filtered_users_sales_order_details.distinct.order( :trade_hub_name ).pluck( :trade_hub_name, :trade_hub_id )

    @item_names = filtered_users_sales_order_details.distinct.order( :eve_item_name )
    @item_names = @item_names.where( trade_hub_id: @selected_trade_hub_id ) if @selected_trade_hub_id
    @item_names = @item_names.pluck( :eve_item_name, :eve_item_id )

    @compared_prices = filtered_users_sales_order_details.order( :trade_hub_name, :eve_item_name )

    @compared_prices = @compared_prices.where( trade_hub_id: @selected_trade_hub_id ) if @selected_trade_hub_id
    @compared_prices = @compared_prices.where( eve_item_id: @selected_eve_item_id ) if @selected_eve_item_id

    lod = @user.last_orders_download ? @user.last_orders_download : Time.at( 0 )
    @data_available_in = (lod + UserSaleOrder::CACHE_DURATION - Time.now).round
  end

  def update
    @user.update( download_orders_running: true )
    DownloadMyOrdersJob.perform_later( @user )
    redirect_to user_sales_orders_path
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