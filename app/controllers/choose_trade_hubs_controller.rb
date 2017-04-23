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
    begin
      ActiveRecord::Base.transaction do

        item = TradeHub.find( params[ :id ] )
        if params[ :check_state ] == 'true'
          @user.trade_hubs << item unless @user.trade_hubs.exists?( id: item.id )
        else
          @user.trade_hubs.delete( item )
        end
        @user.update_attribute(:last_changes_in_choices,Time.now)

      end
    end
    render nothing: true
  end
end
