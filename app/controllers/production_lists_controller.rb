class ProductionListsController < ApplicationController

  before_action :require_logged_in!, :log_client_activity
  before_action :set_user

  def edit
    @title= 'Items you checked in the daily earnings screen'
    @basket_datas = @user.production_lists.includes( {trade_hub: :region}, {eve_item: :blueprint} )
                  .order( :id ).paginate( :page => params[:page], :per_page => 20 )
  end

  # This is used to update the price of a production list item
  def update
    params['runs_count']&.each do |qtt|
      pl = @user.production_lists.find( qtt[0] )
      update_production_list( pl, runs_count: qtt[1] )
    end

    redirect_to edit_production_lists_path
  end

  # This is used to create a production list item
  # Used by Ajax only
  def create
    trade_hub_id = params[:trade_hub_id]
    unless trade_hub_id
      th = TradeHub.find_by_eve_system_id( 30000142 )
      trade_hub_id = th.id
    end
    @user.production_lists.find_or_create_by!(
        trade_hub_id: trade_hub_id, eve_item_id: params[:eve_item_id] )
    head :ok
  end

  def update_from_components_to_buy
    update_from_advice_screen
    redirect_to components_to_buys_path
  end

  def create_from_prices_advices_buy_orders
    create_from_advice_screen
    redirect_to buy_orders_path
  end

  def create_from_prices_advices_immediate
    create_from_advice_screen
    redirect_to price_advices_advice_prices_path
  end

  def create_from_prices_advices_weekly
    create_from_advice_screen
    redirect_to price_advices_advice_prices_weekly_path
  end

  def remove_production_list_check
    # Used by Ajax only
    @user.production_lists.where(
        trade_hub_id: params[:trade_hub_id], eve_item_id: params[:eve_item_id] ).delete_all
    head :ok
  end

  private

  def create_from_advice_screen
    eve_item = EveItem.find( params[:eve_item_id] )

    runs_count = compute_runs_count( eve_item, runs_count: params[:runs_count]&.to_i, quantity: params[:quantity]&.to_i )

    @user.production_lists.create!(
        trade_hub_id: params[:trade_hub_id], eve_item_id: eve_item.id, runs_count: runs_count )
    flash[ :notice ] = 'Production list updated successfully'
  end

  def update_production_list( pl, quantity: nil, runs_count: nil )
    pl.update!( runs_count: compute_runs_count( pl.eve_item, quantity: quantity, runs_count: runs_count ) )
    flash[ :notice ] = 'Production list updated successfully'
  end

  def compute_runs_count( eve_item, quantity: nil, runs_count: nil )
    unless quantity && runs_count
      corresponding_blueprint ||= eve_item.blueprint
      runs_count ||= [ ( quantity.to_f / corresponding_blueprint.prod_qtt ).ceil, corresponding_blueprint.nb_runs ].min
    else
      runs_count= nil
    end
    runs_count
  end

end
