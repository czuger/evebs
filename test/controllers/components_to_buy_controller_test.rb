require 'test_helper'

class ComponentsToBuyControllerTest < ActionDispatch::IntegrationTest

  def setup
    esi_fake_login

    @material_morphite = create( :material_morphite )
    @blueprint = @material_morphite.blueprint
    @blueprint_component = @material_morphite.eve_item

    @eve_item = create( :inferno_fury_cruise_missile, blueprint_id: @blueprint.id )
    @trade_hub = create( :rens )

    @pl = create( :production_list, user_id: @user.id, eve_item_id: @eve_item.id,
                  trade_hub_id: @trade_hub.id, runs_count: 500 )
  end

  test 'should show components' do
    get components_to_buys_url @user
    assert_response :success
  end

  test 'should show components - raw screen' do
    get components_to_buy_show_raw_url @user
    assert_response :success
  end

end
