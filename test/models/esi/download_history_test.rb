require 'test_helper'

class DownloadHistoryTest < ActiveSupport::TestCase

  def setup
    @the_forge = create(:the_forge)

    @dh = Esi::DownloadHistory.new

    @dh.expects(:get_all_pages).with( expect: :region ).returns( 1 )
    @dh.expects(:get_all_pages).with( expect: :record ).returns( [ 1 ] )
  end

  test 'update blueprints' do
    @dh.do_download( [ @the_forge ], 1 )
    assert false
  end

end