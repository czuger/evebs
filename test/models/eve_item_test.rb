require 'test_helper'
require 'pp'
require 'fileutils'
require 'yaml'

class EveItemTest < ActiveSupport::TestCase

  def setup
    create( :jita )
    @item = create( :inferno_fury_cruise_missile )

    FileUtils.cp 'data/type_ids_to_download.yaml', 'data/type_ids_to_download.yaml.backup'
    @esi_data = JSON.parse( File.open( 'test/models/eve_item_test.json', 'r' ).read )
    File.open('data/type_ids_to_download.yaml', 'w') do |f|
      f.write( [ @item.cpp_eve_item_id ].to_yaml )
    end
  end

  def teardown
    FileUtils.cp 'data/type_ids_to_download.yaml.backup', 'data/type_ids_to_download.yaml'
  end

  test 'Download, update and remove item data' do
    d_pto = Esi::DownloadEveItems.new
    d_pto.expects(:get_page).returns(@esi_data)
    d_pto.download

    Process::SetEveItemDepthLevel.new.set

    Process::UpdateEveItems.new().update

    # @esi_data[0]['volume_remain'] = 185
    #
    # d_pto = Esi::DownloadEveItems.new
    # d_pto.expects(:get_page).returns(@esi_data)
    # d_pto.download
    #
    # assert_no_difference 'PublicTradeOrder.count' do
    #   Process::UpdateEveItems.new( silent_output: true ).update
    # end

    # @esi_data.delete( 0 )
    #
    # d_pto = Esi::DownloadEveItems.new
    # d_pto.expects(:get_all_pages).returns(@esi_data)
    # d_pto.download
    #
    # assert_difference 'PublicTradeOrder.count', -1 do
    #   Process::UpdatePublicTradesOrders.new( silent_output: true ).update
    # end
  end

end
