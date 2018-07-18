class ComponentsToBuyController < ApplicationController

  before_action :require_logged_in!, :log_client_activity
  before_action :set_user, only: [:show, :download_assets, :download_assets_start]

  include Modules::SharedPlList

  def show
    # required_quantities_detail = @user.production_lists.where.not( runs_count: nil )
    #     .joins( { eve_item: { blueprint_materials: :blueprint_component } }, { eve_item: :blueprint } )
    #     .pluck( 'eve_items.name', 'blueprint_components.name', :runs_count, :required_qtt )

    # Compute required quantities

    @user = set_user_to_show( @user )

    @required_quantities = @user.production_lists.where.not( runs_count: nil )
        .joins( { eve_item: { blueprint_materials: :blueprint_component } }, { eve_item: :blueprint } )
        .group( 'blueprint_components.id', 'blueprint_components.name' ).sum( 'required_qtt * runs_count' )

    @required_quantities.each do |k, v|
      asset = @user.bpc_assets.where( blueprint_component_id: k[0] ).first
      if asset
        required_quantity = v - asset.quantity
        if required_quantity > 0
          @required_quantities[k] = required_quantity
        else
          @required_quantities.delete( k )
        end
      end
    end

  end

  def download_assets
  end

  def download_assets_start
    @user.update( download_assets_running: true )

    Thread.new { Esi::DownloadMyAssets.new.update( @user ) }

    redirect_to character_download_assets_path( @user )
  end

end
