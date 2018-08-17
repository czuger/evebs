class ProductionListsController < ApplicationController

  before_action :require_logged_in!, :log_client_activity
  before_action :set_user, only: [ :edit, :update, :create, :remove_production_list_check ]

  def edit
    @basket_active_record = @user.production_lists.joins( :trade_hub, :eve_item, { trade_hub: :region } ).
        joins( "LEFT JOIN price_advice_margin_comps pa
                  ON pa.item_id = production_lists.eve_item_id
                  AND pa.trade_hub_id = production_lists.trade_hub_id
                  AND pa.user_id = #{@user.id}" )
                                .order( 'trade_hubs.name', 'eve_items.name' ).paginate( :page => params[:page], :per_page => 20 )

    @basket_array = @basket_active_record.pluck_to_hash( 'trade_hubs.name', 'regions.name', 'eve_items.name', 'eve_items.id',
                                                         :vol_month, :min_price, :single_unit_cost, 'trade_hubs.id',
                                                         :margin_percent, :id, :quantity_to_produce, :batch_size_formula, :full_batch_size )
  end

  # This is used to update the price of a production list item
  def update
    params['quantity_to_produce']&.each do |qtt|
      pl = @user.production_lists.find( qtt[0] )
      unless qtt[1].empty?
        corresponding_blueprint = pl.eve_item.blueprint

        # Always count in production batches
        runs_count = ( qtt[1].to_f / corresponding_blueprint.prod_qtt ).ceil
        quantity_to_produce = runs_count * corresponding_blueprint.prod_qtt
        pl.update!( quantity_to_produce: quantity_to_produce, runs_count: runs_count )
      else
        pl.update!( quantity_to_produce: nil, runs_count: nil )
      end
    end

    flash[ :notice ] = 'Production list updated successfully'

    redirect_to edit_production_list_path( @user )
  end

  # This is used to create a production list item
  # Used by Ajax only
  def create
    @user.production_lists.find_or_create_by!(
        trade_hub_id: params[:trade_hub_id], eve_item_id: params[:eve_item_id] )
    head :ok
  end

  def remove_production_list_check
    # Used by Ajax only
    @user.production_lists.where(
        trade_hub_id: params[:trade_hub_id], eve_item_id: params[:eve_item_id] ).delete_all
    head :ok
  end

end
