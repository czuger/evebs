require 'time_diff'

class PriceAdvicesController < ApplicationController

  before_action :require_logged_in!

  include PriceAdviceMonthly
  include PriceAdviceDaily

  def show_challenged_prices

    @user = current_user
    @print_change_warning=print_change_warning

    @trade_orders = @user.trade_orders
    @compared_prices = []

    @trade_orders.each do |to|
      min_price = MinPrice.find_by_eve_item_id_and_trade_hub_id( to.eve_item_id, to.trade_hub_id )

      min_price = min_price.min_price if min_price

      prod_qtt = to.eve_item.blueprint.prod_qtt
      cost = to.eve_item.cost / prod_qtt
      margin_pcent = ( min_price / cost ) - 1 if cost && min_price

      @compared_prices << {
          trade_hub_name: to.trade_hub.name, eve_item_name: to.eve_item.name, my_price: to.price,
          min_price: min_price, cost: cost, margin_pcent: margin_pcent
      }
    end

    @compared_prices = @compared_prices.sort_by{ |e| [e[:trade_hub_name], e[:eve_item_name]] }

  end

  def show_item_in_trade_hub

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
  def get_montly_items_averages
    datas = CrestPricesLastMonthAverage.where( eve_item_id: @user.eve_items, region_id: @user.regions.pluck(:id) ).to_a
    Hash[datas.map{ |e| [[[e.region_id],[e.eve_item_id]],e]}]
  end
end

