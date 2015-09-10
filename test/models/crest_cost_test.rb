require 'test_helper'

class CrestCostTest < ActiveSupport::TestCase

  test "Get crest for morphite in jita" do
    Crest::GetPriceHistory.get( 10000002, 16680, )
  end

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

  test "Test crest item should load a morphite and phenolic composite object" do
    Crest::EveItemsFromCrest.update_eve_items

    assert EveItem.find_by_cpp_eve_item_id( 11399 )
    assert EveItem.find_by_cpp_eve_item_id( 16680 )
  end

end
