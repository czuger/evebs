require 'test_helper'

class MarketGroupTest < ActiveSupport::TestCase

  def setup
    create( :inferno_fury_cruise_missile )
    create( :mjolnir_fury_cruise_missile )
  end

  test 'items_tree.json should be created and not empty' do

    MarketGroup.stubs( :roots ).returns( [ MarketGroup.new ] )

    MarketGroup.build_items_tree

    assert_not_equal 0, File.open( 'public/items_tree.json', 'r' ).size
  end

end
