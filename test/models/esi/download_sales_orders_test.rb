require 'test_helper'

class DownloadSalesOrdersTest < ActiveSupport::TestCase

  def setup
    jita = create( :jita )
    item = create( :morphite )
    bpc_item = create( :component_morphite )

    @dso = Esi::DownloadSalesOrders.new( silent_output: true )
    @base_so_record = {
        'system_id' => jita.eve_system_id, 'type_id' => item.cpp_eve_item_id, 'price' => 100, 'volume_remain' => 5000,
        'order_id' => 1, 'issued' => "2018-07-16T15:18:28Z", 'duration' => 90, 'volume_total' => 10000 }
    @records_to_return = [ @base_so_record ]
    @dso.stubs( :get_all_pages ).returns( @records_to_return )
  end

  test 'Non existing record' do
    assert_difference 'BlueprintComponentSalesOrder.count' do
      assert_difference 'SalesFinal.count' do
        assert_difference 'SalesOrder.count' do
          @dso.update
          # pp SalesOrder.all
        end
      end
    end

    assert_equal '2018-07-16T15:18:28',  SalesOrder.first.issued.strftime('%Y-%m-%dT%H:%M:%S')
  end

  test 'Update existing record' do
    @dso.update
    @base_so_record['volume_remain'] = 2000
    assert_no_difference 'BlueprintComponentSalesOrder.count' do
      assert_difference 'SalesFinal.count' do
        assert_no_difference 'SalesOrder.count' do
          @dso.update
        end
      end
    end
  end

  test 'multiple records for single order_id not existing record - volumes in bad order' do
    base_so_record_cp = @base_so_record.dup
    base_so_record_cp[ 'volume_remain' ] = 6000
    @records_to_return << base_so_record_cp

    assert_difference 'BlueprintComponentSalesOrder.count' do
      assert_difference 'SalesFinal.count', 2 do
        assert_difference 'SalesOrder.count' do
          @dso.update
        end
      end
    end

    assert_equal 5000, SalesOrder.first.reload.volume
  end

  test 'should touch only the record' do
    @dso.update
    assert_no_difference 'BlueprintComponentSalesOrder.count' do
      assert_no_difference 'SalesFinal.count'do
        assert_no_difference 'SalesOrder.count' do
          @dso.update
        end
      end
    end
  end

  test 'should removed record. if time is not issued should not create a sale final record' do
    @base_so_record['issued'] = Time.now.strftime('%F')
    @dso.update

    @records_to_return = []
    @dso.stubs( :get_all_pages ).returns( @records_to_return )

    assert_difference 'BlueprintComponentSalesOrder.count', -1 do
      assert_no_difference 'SalesFinal.count'do
        assert_difference 'SalesOrder.count', -1 do
          @dso.update
        end
      end
    end
  end

  test 'should removed record. if time is issued should create a sale final record' do
    @base_so_record['issued'] = ( Time.now - 1.year ).strftime('%F')
    @dso.update

    @records_to_return = []
    @dso.stubs( :get_all_pages ).returns( @records_to_return )

    assert_difference 'BlueprintComponentSalesOrder.count', -1 do
      assert_difference 'SalesFinal.count'do
        assert_difference 'SalesOrder.count', -1 do
          @dso.update
        end
      end
    end
  end

end