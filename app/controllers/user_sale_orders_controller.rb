class UserSaleOrdersController < ApplicationController

  before_action :require_logged_in!, :log_client_activity
  before_action :set_user, only: [
      :index, :download_orders, :download_orders_start, :send_my_orders_edit, :send_my_orders, :get_sent_orders ]

  def index
    @orders_active_record = @user.user_sale_orders.joins( :eve_item, trade_hub: :region )
      .order( 'trade_hubs.name', 'eve_items.name' ).paginate( :page => params[:page], :per_page => 20 )

    @orders_data = @orders_active_record.pluck_to_hash(
        'trade_hubs.name', 'regions.name', 'eve_items.name', 'eve_items.id', :price )

  end

  def show_challenged_prices
    @user = current_user
    @print_change_warning=print_change_warning

    @trade_orders = @user.user_sale_orders.includes( { eve_item: :blueprint }, { trade_hub: :region } )
    @compared_prices = []

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
  end

  def download_orders
  end

  def download_orders_start
    @user.update( download_orders_running: true )

    DownloadMyOrdersJob.perform_later( @user )

    redirect_to download_orders_path
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