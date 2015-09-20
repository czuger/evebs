require 'test_helper'

class MarketGroupTest < ActiveSupport::TestCase

  def setup
    create( :inferno_fury_cruise_missile )
    create( :mjolnir_fury_cruise_missile )
  end

  test "the truth" do
    Crest::MarketGroups.update_market_group
    pp MarketGroup.all
  end

end
