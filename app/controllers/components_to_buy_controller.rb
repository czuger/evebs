class ComponentsToBuyController < ApplicationController

  before_action :require_logged_in!, :log_client_activity
  before_action :set_user
  before_action :set_required_quantities, only: [ :show, :components_to_buy_show_raw ]

  def show
    @total_volume = @required_quantities.sum( :required_volume ).ceil
    @total_isk = @required_quantities.sum( :total_cost ).ceil
  end

  def components_to_buy_show_raw
    render layout: false
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
    @required_quantities = @user.selected_assets_station_id ? @user.component_to_buys.where( user_id: @user.id ) : ComponentToBuy.none
  end

end
