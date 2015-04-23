class ChooseTradeHubsController < ApplicationController

  def edit
    @user = current_user
    @trade_hubs = TradeHub.all.to_a
    @user_trade_hubs_ids = @user.trade_hubs.map{ |e| e.id }
  end

  def update
    @user = current_user
    ActiveRecord::Base.transaction do
      @user.trade_hub_ids = params['trade_hubs_ids']
      @user.update_attribute(:last_changes_in_choices,Time.now)
    end
    redirect_to edit_choose_trade_hubs_path
  end
end
