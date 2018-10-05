class ComponentsToBuysController < ApplicationController

  before_action :require_logged_in!, :log_client_activity
  before_action :set_user
  before_action :set_required_quantities, only: [ :show, :components_to_buy_show_raw ]

  def show
    @jita = TradeHub.find_by_eve_system_id( 30000142 )

    @total_isk = @required_quantities.map{ |e| e.quantity * e.eve_item.cost }.inject( &:+ )
    @total_volume = @required_quantities.map{ |e| e.quantity * e.eve_item.volume }.inject( &:+ )&.round(1)
  end

  def components_to_buy_show_raw
    render layout: false
  end

  def update
    ComponentsToBuy.refresh_components_to_buy_list_for( @user )
    redirect_to components_to_buys_path
  end

  def download_assets
  end

  def download_assets_start
    @user.update( download_assets_running: true )

    # has to be before DownloadMyAssets
    DownloadMyAssetsJob.perform_later( @user )

    redirect_to character_download_assets_path( @user )
  end

  private

  def set_required_quantities
    @required_quantities = @user.components_to_buys.includes( :eve_item ) # ? @user.component_to_buys : ComponentsToBuy.none
  end

end
