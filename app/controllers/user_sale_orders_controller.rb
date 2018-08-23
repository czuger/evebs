class UserSaleOrdersController < ApplicationController

  before_action :require_logged_in!, :log_client_activity
  before_action :set_user

  def show
    @user = current_user
    @print_change_warning=print_change_warning

    @trade_orders = @user.user_sale_orders.includes( { eve_item: :blueprint }, { trade_hub: :region } )
    @compared_prices = []

    mp_keys = @trade_orders.map{ |to| [ to.eve_item_id, to.trade_hub_id ] }
    mp_results = PricesMin.where( )

    @trade_orders.each do |to|
      min_price = PricesMin.find_by_eve_item_id_and_trade_hub_id(to.eve_item_id, to.trade_hub_id )

      min_price = min_price.min_price if min_price

      prod_qtt = to.eve_item.blueprint.prod_qtt
      cost = to.eve_item.cost / prod_qtt
      margin_pcent = ( min_price / cost ) - 1 if cost && min_price

      trade_hub_name = "#{to.trade_hub.name} (#{to.trade_hub.region&.name})"

      @compared_prices << {
          trade_hub_name: trade_hub_name, eve_item_name: to.eve_item.name, my_price: to.price,
          min_price: min_price, cost: cost, margin_pcent: margin_pcent, eve_item_id: to.eve_item_id,
          eve_item_cpp_id: to.eve_item.cpp_eve_item_id, trade_hub_cpp_id: to.trade_hub.eve_system_id
      }

      set_trade_hubs( trade_hub_name )
      set_items( to.eve_item.name )
    end

    @compared_prices = @compared_prices.sort_by{ |e| [e[:trade_hub_name], e[:eve_item_name]] }

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

  def set_trade_hubs( trade_hub_name )
    @trade_hubs_names = [] unless @trade_hubs_names
    @trade_hubs_names << trade_hub_name unless @trade_hubs_names.include?( trade_hub_name )
    @trade_hubs_names.sort!
  end

  def set_items( item_name )
    @item_names = [] unless @item_names
    @item_names << item_name unless @item_names.include?( item_name )
    @item_names.sort!
  end

end