class ShoppingBasketsController < ApplicationController

  before_action :require_logged_in!, :log_client_activity

  def show
    @user = current_user
    @basket = ShoppingBasket.where( user_id: @user ).includes( :trade_hub, :eve_item ).order( 'trade_hubs.name', 'eve_items.name' )
  end

end
