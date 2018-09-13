require 'test_helper'

class ComponentToBuyTest < ActiveSupport::TestCase

  def setup
    create( :inferno_fury_cruise_missile_production_list )
    create( :mjolnir_fury_cruise_missile_production_list )
  end

  def test_base_components_request
    ctb = ComponentToBuy.find_by_name( 'Morphite' )
    assert 1200, ctb.total_cost
    assert 0.15, ctb.required_volume
  end

end