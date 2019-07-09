require 'test_helper'

class AssetsControllerTest < ActionDispatch::IntegrationTest

  def setup
    @user = create( :user )
    post '/auth/developer/callback', params: { name: @user.name }

    # @trade_hub = create( :jita )
    @station = create( :station_detail )
  end

  test 'should show' do
    get my_assets_path
    assert_response :success
  end

  test 'should start downloading my assets' do
    patch my_assets_path
    assert_redirected_to my_assets_path
  end

  test 'should set my asset station id' do
    post set_assets_station_my_assets_path, params: { asset_station_id: @station.id }
    assert_redirected_to my_assets_path
  end


end
