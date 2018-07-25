require 'test_helper'

class DownloadSalesOrdersTest < ActiveSupport::TestCase

  def setup
    jita = create( :jita )
    item = create( :inferno_fury_cruise_missile )

    @dso = Esi::DownloadSalesOrders.new( silent_output: true )
    @dso.stubs( :get_all_pages ).returns( [] )
    @base_so_record = {
        'system_id' => jita.eve_system_id, 'type_id' => item.cpp_eve_item_id, 'price' => 100, 'volume_remain' => 5000,
        'order_id' => 1, 'issued' => "2018-07-16T15:18:28Z", 'duration' => 90, 'volume_total' => 10000
    }
  end

  test 'basic test' do
    @dso.stubs( :get_all_pages ).returns( [ @base_so_record ] )
    @dso.update
  end

end