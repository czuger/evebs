require 'test_helper'

class DownloadHistoryTest < ActiveSupport::TestCase

  def setup
    @the_forge = create(:the_forge)

    @dh = Esi::DownloadHistory.new

    @dh.expects(:get_all_pages).with( expect: :region ).returns(
      [ :dummy ] )
    @dh.expects(:get_all_pages).with( expect: :record ).returns(
      [ { 'date' => Time.now.to_s, 'volume' => 50, 'lowest' => 1, 'highest' => 100, 'average' => 50 } ] )
  end

  test 'update blueprints' do
    # Just a code test
    @dh.do_download( [ @the_forge ], 1 )
  end

end