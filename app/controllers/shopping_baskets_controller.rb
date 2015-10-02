class ShoppingBasketsController < ApplicationController

  def show
    @user = current_user
    @basket = ShoppingBasket.where( user_id: @user ).includes( :trade_hub, :eve_item ).order( 'trade_hubs.name', 'eve_items.name' )
  end

end
