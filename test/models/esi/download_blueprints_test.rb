require 'test_helper'

class DownloadBlueprintsTest < ActiveSupport::TestCase

  def setup
    @ub = Esi::UpdateBlueprints.new
    @ub.stubs( :open ).returns( [] )
  end

  # test 'update blueprints' do
  #   @ub.update
  # end

end