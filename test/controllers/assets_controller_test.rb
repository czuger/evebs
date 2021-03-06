require 'test_helper'

class AssetsControllerTest < ActionDispatch::IntegrationTest

  def setup
    esi_fake_login

    @user = create( :user, last_assets_download: Time.now )

    create( :vellaine_system )
    @asset = create( :bpc_asset, user: @user )

    @user.selected_assets_station_id = @asset.universe_station_id
    @user.save!
  end

  # test 'should show' do
  #   get my_assets_path
  #   assert_response :success
	#
  #   assert_select 'td', 'Vellaine VI - Moon 9 - Propel Dynamics Factory'
  #   assert_select 'td', 'Inferno Fury Cruise Missile'
  #   # assert_select 'td', '5689'
  # end

  test 'should start downloading my assets' do
    assert_enqueued_with(job: DownloadMyAssetsJob) do
      patch my_assets_path
    end
    assert_redirected_to my_assets_path
  end

  test 'should set my asset station id' do
    post set_assets_station_my_assets_path, params: { asset_station_id: @asset.universe_station_id }
    assert_redirected_to my_assets_path
  end

end
