require 'test_helper'

class EveItemTest < ActiveSupport::TestCase

  test "Inferno Precision Cruise Missile should retrieve a min price for Rens" do
    trade_hub = create( :rens )
    eve_item = create( :inferno_precision_cruise_missile )
    EveItem.compute_min_price_for_system( trade_hub, [ eve_item ] )
  end
end
