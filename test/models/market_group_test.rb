require 'test_helper'

class MarketGroupTest < ActiveSupport::TestCase

  def setup
    @blueprint = create( :blueprint )

    create( :inferno_fury_cruise_missile, blueprint_id: @blueprint.id  )
    create( :mjolnir_fury_cruise_missile, blueprint_id: @blueprint.id  )
  end

  test 'items_tree.json should be created and not empty' do

    MarketGroup.stubs( :roots ).returns( [ MarketGroup.new ] )

    `cp data/items_tree.json data/items_tree.json.bckp`

    MarketGroup.build_items_tree

    assert_not_equal 0, File.open( 'data/items_tree.json', 'r' ).size

    `cp data/items_tree.json.bckp data/items_tree.json`
    `rm data/items_tree.json.bckp`
  end

end
