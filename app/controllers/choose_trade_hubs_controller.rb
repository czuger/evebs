class ChooseTradeHubsController < ApplicationController
  def edit
    @user = User.first
    @trade_hubs = TradeHub.all.to_a
    @user_trade_hubs_ids = @user.trade_hubs.map{ |e| e.id }
  end

  def update
    @user = User.first
    @user.trade_hub_ids = params['trade_hubs_ids']
    redirect_to edit_choose_trade_hub_path(@user.id)
  end
end
