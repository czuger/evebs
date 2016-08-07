require 'test_helper'

class InitRegionTest < ActiveSupport::TestCase

  test "Should do something" do
    Object.stubs( :read ).returns( { items: [ { name: 'test', href: '/1/' } ] }.to_json )

    c = Crest::InitRegions.new
    c.stubs( :open ).returns( Object )
    c.stubs( :link_region_to_trade_hub )

    c.fill_regions
  end

end
