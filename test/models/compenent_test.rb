require 'test_helper'

class CompenentTest < ActiveSupport::TestCase

  test 'Should set min prices for all components' do
    create( :inferno_precision_cruise_missile )
    BlueprintComponent.compute_costs
    # TODO : make a real assert there
  end

end
