require 'test_helper'

class DownloadMyAssetsTest < ActiveSupport::TestCase

  def setup
    @jita = create( :jita )
    @user = create( :user, selected_assets_station_id: @jita_id )

    @vellaine = create( :vellaine )
    create( :bpc_assets_station, user: @user, universe_station: @vellaine )

    @cm = create( :inferno_fury_cruise_missile )

    @esi_data = JSON.parse(
        <<-ESI_DATA
    [
        {
            "quantity": 90,
            "touched": true,
            "type_id": #{@cm.cpp_eve_item_id},
            "location_id": #{@vellaine.cpp_station_id}
        }
    ]
    ESI_DATA
    )
  end

  test 'Download new asset and then update it and then remove it' do
    d_pto = Esi::DownloadMyAssets.new
    d_pto.stubs(:set_auth_token).returns(true)
    d_pto.stubs(:get_all_pages).returns(@esi_data)

    assert_difference 'BpcAsset.count' do
      d_pto.update( @user )
    end
    assert_equal 90,BpcAsset.first.quantity

    @esi_data.first[ 'quantity' ] = 100
    assert_no_difference 'BpcAsset.count' do
      d_pto.update( @user )
    end
    assert_equal 100,BpcAsset.first.quantity

    @esi_data.clear
    assert_difference 'BpcAsset.count', -1 do
      d_pto.update( @user )
    end
  end

end