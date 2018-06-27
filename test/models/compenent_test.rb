require 'test_helper'

class CompenentTest < ActiveSupport::TestCase

  test 'Should set min prices for all components' do
    create( :inferno_precision_cruise_missile )
    BlueprintComponent.set_min_prices_for_all_components
    # TODO : make a real assert there
  end

end
