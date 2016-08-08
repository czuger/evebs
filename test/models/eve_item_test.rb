require 'test_helper'
require 'pp'

class EveItemTest < ActiveSupport::TestCase

  test 'Should set cost to nil when no material cost' do
    eve_item = create( :dummy_eve_item )
    eve_item.compute_cost
    refute eve_item.cost
  end

  test 'Should recompute cost for the given item' do
    eve_item = create( :inferno_precision_cruise_missile )
    eve_item.compute_cost
    assert 427510.0, eve_item.cost
  end

  test 'Inferno Precision Cruise Missile should retrieve a min price for Rens' do

    trade_hub = create( :rens )
    eve_item = create( :inferno_precision_cruise_missile )

    Object.stubs( :read ).returns( [ { 'sell' => { 'min' => 5, 'forQuery' => { 'types' => [ eve_item.cpp_eve_item_id ] }}} ].to_json )
    EveItem.stubs( :open ).returns( Object )
    EveItem.compute_min_price_for_system( trade_hub, [ eve_item ] )
  end

end
