class ProductionListsController < ApplicationController

  before_action :require_logged_in!, :log_client_activity
  before_action :set_user, only: [:edit, :update, :share_list, :share_list_update, :accept_shared_list,
                                       :accept_shared_list_update]

  include Modules::SharedPlList

  def edit
    user_to_show = set_user_to_show( @user )

    @basket_active_record = user_to_show.production_lists.joins( :trade_hub, :eve_item, { trade_hub: :region } ).
        joins( 'LEFT JOIN prices_advices ON prices_advices.eve_item_id = production_lists.eve_item_id AND prices_advices.trade_hub_id = production_lists.trade_hub_id' )
                                .order( 'trade_hubs.name', 'eve_items.name' ).paginate( :page => params[:page], :per_page => 20 )

    @basket_array = @basket_active_record.pluck_to_hash( 'trade_hubs.name', 'regions.name', 'eve_items.name', 'eve_items.id',
                                                         :vol_month, :min_price, :single_unit_cost, 'trade_hubs.id',
                                                         :margin_percent, :id, :quantity_to_produce )
  end

  def update
    params['quantity_to_produce']&.each do |qtt|
      unless qtt[1].empty?

        @user = set_user_to_show( @user )
        pl = @user.production_lists.find( qtt[0] )
        corresponding_blueprint = pl.eve_item.blueprint

        # Always count in production batches
        runs_count = ( qtt[1].to_f / corresponding_blueprint.prod_qtt ).ceil
        quantity_to_produce = runs_count * corresponding_blueprint.prod_qtt
        pl.update!( quantity_to_produce: quantity_to_produce, runs_count: runs_count )
      end
    end

    flash[ :notice ] = 'Production list updated successfully'

    redirect_to edit_production_list_path( @user )
  end

  def share_list
    @users = User.where.not( id: @user.id ).pluck( :name, :id )
  end

  def share_list_update
    ProductionListShareRequest.find_or_create_by!( sender_id: params[:user_id].to_i, recipient_id: params[:user][:id].to_i )
    flash[ :notice ] = 'List sent successfully'
    redirect_to character_share_list_path( @user )
  end

  def accept_shared_list
    @shared_lists = ProductionListShareRequest.joins( :sender ).where( recipient_id: @user.id ).pluck( 'users.name', 'users.id' )
  end

  def accept_shared_list_update
    ActiveRecord::Base.transaction do
      @user.production_lists.clear
      @user.user_pl_share_id = params['sending_user_id']
      @user.save!

      ProductionListShareRequest.where( recipient_id: @user.id, sender_id: params['sending_user_id'] ).delete_all
    end

    flash[ :notice ] = 'List successfully linked'
    redirect_to character_accept_shared_list_path( @user )
  end

end
