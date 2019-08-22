require 'test_helper'

class PublicTradeOrderTest < ActiveSupport::TestCase

  def setup
    create( :universe_jita )
    @cm = create( :inferno_fury_cruise_missile )

    @esi_data = JSON.parse(
    <<-ESI_DATA
    [
        {
            "duration": 90,
            "is_buy_order": false,
            "issued": "2019-06-06T13:00:05Z",
            "location_id": 60003760,
            "min_volume": 1,
            "order_id": 5440012287,
            "price": 33000,
            "range": "region",
            "system_id": 30000142,
            "type_id": #{@cm.cpp_eve_item_id},
            "volume_remain": 190,
            "volume_total": 190
        },
        {
            "duration": 14,
            "is_buy_order": false,
            "issued": "2019-07-10T03:23:48Z",
            "location_id": 60003760,
            "min_volume": 1,
            "order_id": 5460983807,
            "price": 81880001.05,
            "range": "region",
            "system_id": 30000142,
            "type_id": 999,
            "volume_remain": 1,
            "volume_total": 3
        },
        {
            "duration": 14,
            "is_buy_order": false,
            "issued": "2019-07-10T03:23:48Z",
            "location_id": 60003760,
            "min_volume": 1,
            "order_id": 5460983808,
            "price": 81880001.05,
            "range": "region",
            "system_id": 999,
            "type_id": #{@cm.cpp_eve_item_id},
            "volume_remain": 1,
            "volume_total": 3
        }
    ]
    ESI_DATA
    )
  end

  test 'Download and update for new orders' do
    d_pto = Esi::DownloadPublicTradesOrders.new
    d_pto.expects(:get_all_pages).returns(@esi_data)
    d_pto.download

    assert_difference 'PublicTradeOrder.count' do
      Process::UpdatePublicTradesOrders.new.update
    end
  end

  test 'Download and update and test orders modifications' do
    d_pto = Esi::DownloadPublicTradesOrders.new
    d_pto.expects(:get_all_pages).returns(@esi_data)
    d_pto.download

    Process::UpdatePublicTradesOrders.new.update

    @esi_data[0]['volume_remain'] = 185

    d_pto = Esi::DownloadPublicTradesOrders.new
    d_pto.expects(:get_all_pages).returns(@esi_data)
    d_pto.download

    assert_no_difference 'PublicTradeOrder.count' do
      Process::UpdatePublicTradesOrders.new.update
    end
  end

end
