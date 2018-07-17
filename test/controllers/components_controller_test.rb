require 'test_helper'

class ComponentsControllerTest < ActionDispatch::IntegrationTest

  def setup
    @component = create( :component_morphite )
  end

  test 'should get show' do
    get component_url( @component )
    assert_response :success
  end

  test 'should get index' do
    get components_url
    assert_response :success
  end

  test 'should get component_trade_hub_detail' do
    @trade_hub = create( :pator )
    get component_trade_hub_detail_url( @component, trade_hub_id: @trade_hub.id )
    assert_response :success
  end

end
