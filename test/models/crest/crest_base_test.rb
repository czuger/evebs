require 'test_helper'

class CrestBaseTest < ActiveSupport::TestCase

  include Crest::CrestBase

  test "Should load blueprint array" do
    get_multipage_data( 'market/10000002/types/34/history', true )
  end

end
