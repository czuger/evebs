require 'test_helper'
require 'pp'

class EveItemTest < ActiveSupport::TestCase

  test "Inferno Precision Cruise Missile should retrieve a min price for Rens" do

    trade_hub = create( :rens )
    eve_item = create( :inferno_precision_cruise_missile )

    Object.stubs( :read ).returns( [ { 'sell' => { 'min' => 5, 'forQuery' => { 'types' => [ eve_item.cpp_eve_item_id ] }}} ].to_json )
    EveItem.stubs( :open ).returns( Object )
    EveItem.compute_min_price_for_system( trade_hub, [ eve_item ] )
  end
end
