class ComponentsToBuyController < ApplicationController

  before_action :require_logged_in!, :log_client_activity
  before_action :set_user, only: [:show, :download_assets, :download_assets_start, :components_to_buy_show_raw]

  def show
    @required_quantities = @user.component_to_buys
    @total_volume = @user.component_to_buys.sum( :required_volume ).ceil
    @total_isk = @user.component_to_buys.sum( :total_cost ).ceil
  end

  def components_to_buy_show_raw
    @required_quantities = @user.component_to_buys
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

end
