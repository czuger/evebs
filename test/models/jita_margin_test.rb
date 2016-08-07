require 'test_helper'

class JitaMarginTest < ActiveSupport::TestCase

  test "Should compute jita margins prices" do

    eve_item = create( :inferno_precision_cruise_missile )
    jita = create( :jita )
    create( :min_price, eve_item_id: eve_item.id, trade_hub_id: jita.id )

    JitaMargin.compute_margins()

  end

end
