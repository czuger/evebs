class ProductionListsController < ApplicationController

  before_action :require_logged_in!, :log_client_activity
  before_action :set_character, only: [:edit, :update, :share_list, :share_list_update]

  def edit
    @basket_active_record = @user.production_lists.joins( :trade_hub, :eve_item, { trade_hub: :region } ).
        joins( 'LEFT JOIN prices_advices ON prices_advices.eve_item_id = production_lists.eve_item_id AND prices_advices.trade_hub_id = production_lists.trade_hub_id' )
                                .order( 'trade_hubs.name', 'eve_items.name' ).paginate( :page => params[:page], :per_page => 20 )

    @basket_array = @basket_active_record.pluck_to_hash( 'trade_hubs.name', 'regions.name', 'eve_items.name', 'eve_items.id',
                                                         :vol_month, :min_price, :single_unit_cost, 'trade_hubs.id',
                                                         :margin_percent, :id, :quantity_to_produce )
  end

  def update
    params['quantity_to_produce'].each do |qtt|
      unless qtt[1].empty?
        pl = @user.production_lists.find( qtt[0] )
        corresponding_blueprint = pl.eve_item.blueprint

        # Always count in production batches
        runs_count = ( qtt[1].to_f / corresponding_blueprint.prod_qtt ).ceil
        quantity_to_produce = runs_count * corresponding_blueprint.prod_qtt
        pl.update!( quantity_to_produce: quantity_to_produce, runs_count: runs_count )
      end
    end

    redirect_to edit_production_list_path( @character )
  end

  def share_list
    @characters = Character.all.pluck( :name, :id )
  end

  def share_list_update
    params[:character][:id].to_i
    params[:character_id].to_i
    ProductionListShareRequest.find_or_create_by!( sender_id: params[:character_id].to_i, recipient_id: params[:character][:id].to_i )
    flash[ :notice ] = 'List sent successfully'
    redirect_to character_share_list_path( @character )
  end

  def accept_shared_list
  end

  private

    def set_character
      @character = Character.find( params[:id] || params[:character_id] )
      @user = @character.user
    end

    # Never trust parameters from the scary internet, only allow the white list through.
    def character_params
      params.require(:character).permit( :download_my_assets, :locked )
    end

end
