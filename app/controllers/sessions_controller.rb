require 'pp'

class SessionsController < ApplicationController

  before_action :log_client_activity

  def new
    # @prices_array=[]
    # user = User.find_by_name('PUBLIC_USER')
    # user.trade_hubs.each do |trade_hub|
    #   eve_items = user.eve_items.to_a
    #
    #   min_price_items = MinPrice.includes(eve_item:[:blueprint]).where( { eve_item_id: eve_items.map{ |i| i.id }, trade_hub_id: trade_hub.id } )
    #   min_price_items.each do |min_price_item|
    #
    #     blueprint = min_price_item.eve_item.blueprint
    #     batch_size = blueprint.nb_runs*blueprint.prod_qtt
    #     batch_cost = min_price_item.eve_item.cost*blueprint.nb_runs
    #     batch_sell_price = min_price_item.min_price*batch_size
    #     benef = batch_sell_price - batch_cost
    #     benef_pcent = ((batch_sell_price*100) / batch_cost).round(0)-100
    #
    #       @prices_array << {
    #           trade_hub: trade_hub.name,
    #           eve_item: min_price_item.eve_item.name,
    #           min_price: min_price_item.min_price.round(1),
    #           cost: (min_price_item.eve_item.cost/blueprint.prod_qtt).round(1),
    #           benef: benef,
    #           benef_pcent: benef_pcent,
    #           batch_size: batch_size
    #       }
    #   end
    # end
    # @prices_array.sort_by!{ |h| h[:benef] }
    # @prices_array.reverse!
    # @prices_array = @prices_array.shift(3)
    @eve_items_count = EveItem.count
    @trade_hubs_count = TradeHub.count
  end

  def create
    user = User.from_omniauth(env["omniauth.auth"])
    raise "User can't be found : #{user}" unless user
    session[:user_id] = user.id
    redirect_to price_advices_advice_prices_url
  end

  def destroy
    session[:user_id] = nil
    redirect_to root_url
  end

  def failure
    redirect_to new_sessions_path, alert: "Authentication failed, please try again."
  end

  # def screenshots
  #   @picture_names = %w( add_items edit_items_list choose_trade_hubs advice_prices edit_user )
  #   @picture_legends = [
  #     "Add items", "Edit items list", "Choose trade hubs", "Advice prices", "Edit user" ]
  # end

end