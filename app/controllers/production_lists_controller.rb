class ProductionListsController < ApplicationController

  before_action :require_logged_in!, :log_client_activity
  before_action :set_user

  def edit
    # @basket_active_record = @user.production_lists.joins( { trade_hub: :region }, { eve_item: :blueprint } ).
    #     joins( "LEFT JOIN price_advice_margin_comps pa
    #               ON pa.item_id = production_lists.eve_item_id
    #               AND pa.trade_hub_id = production_lists.trade_hub_id
    #               AND pa.user_id = #{@user.id}" )
    #                             .order( 'trade_hubs.name', 'eve_items.name' ).paginate( :page => params[:page], :per_page => 20 )

    # @basket_array = @basket_active_record.pluck_to_hash( 'trade_hubs.name', 'regions.name', 'eve_items.name', 'eve_items.id',
    #                                                      :vol_month, :min_price, :single_unit_cost, 'trade_hubs.id',
    #                                                      :margin_percent, :id, :quantity_to_produce, :batch_size_formula,
    #                                                      :full_batch_size )

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

  # def update_from_buy_orders
  #   update_from_advice_screen
  #
  #   redirect_to buy_orders_path
  # end
  #
  # def update_from_prices_advices
  #   update_from_advice_screen
  #
  #   if params[:margin_type] == 'daily'
  #     redirect_to price_advices_advice_prices_path
  #   else
  #     redirect_to price_advices_advice_prices_weekly_path
  #   end
  # end

  def remove_production_list_check
    # Used by Ajax only
    @user.production_lists.where(
        trade_hub_id: params[:trade_hub_id], eve_item_id: params[:eve_item_id] ).delete_all
    head :ok
  end

  private

  # def update_from_advice_screen
  #   production_entry = @user.production_lists.where(
  #       trade_hub_id: params[:trade_hub_id], eve_item_id: params[:eve_item_id] ).first_or_initialize
  #
  #   update_production_list production_entry, runs_count: params[:runs_count]&.to_i, quantity: params[:quantity]&.to_i
  # end
  #

  def update_production_list( pl, quantity: nil, runs_count: nil )
    unless quantity && runs_count

      corresponding_blueprint ||= pl.eve_item.blueprint
      runs_count ||= [ ( quantity.to_f / corresponding_blueprint.prod_qtt ).ceil, corresponding_blueprint.nb_runs ].min

      pl.update!( runs_count: runs_count )
    else
      pl.update!( runs_count: nil )
    end

    flash[ :notice ] = 'Production list updated successfully'
  end

end
