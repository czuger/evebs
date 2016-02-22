class ChooseTradeHubsController < ApplicationController

  before_action :require_logged_in!, :log_client_activity

  def edit
    @user = current_user
    @inner_trade_hubs = TradeHub.includes(:region).where( inner: true ).where.not( region: nil ).order(:region_id, :name).to_a
    @outer_trade_hubs = TradeHub.includes(:region).where( inner: false ).where.not( region: nil ).order(:region_id, :name).to_a
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
