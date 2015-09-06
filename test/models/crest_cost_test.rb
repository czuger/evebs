require 'test_helper'

class CrestCostTest < ActiveSupport::TestCase
  test "Test crest cost for inferno fury cruise missile" do

    create( :inferno_fury_cruise_missile )
    create( :morphite )
    create( :rocket_fuel )
    create( :ram_amunition_tech )
    create( :component_phenolic_composite )
    create( :plasma_pulse_generator )

    Crest::AverageMarketPrices.get_prices
    Crest::AverageMarketPrices.update_prices
  end
end
