require 'test_helper'

class PriceAdvicesControllerTest < ActionDispatch::IntegrationTest

  def setup
    @user = create( :user )
    post '/auth/developer/callback', params: { name: @user.name }

    @blueprint = create( :blueprint )

    @eve_item = create( :inferno_fury_cruise_missile, blueprint_id: @blueprint.id )
    @trade_hub = create( :rens )
    # Sql::PricesAdvices.update
  end

  test 'should show prices for current user' do
    get price_advices_advice_prices_url
    assert_response :success
  end

  test 'should show prices for current user with last months averages' do
    get price_advices_advice_prices_url
    assert_response :success
  end

  test 'should show prices for current user for Great Wildlands (had a bug)' do
    great_wildlands = create( :e02_ik )
    @user.trade_hubs << great_wildlands
    get price_advices_advice_prices_url
    assert_response :success
  end

  test 'should advice monthly prices' do
    get price_advices_advice_prices_monthly_url
    assert_response :success
  end

  # test 'should show challenged prices without min prices' do
  #   PricesMin.find_by_eve_item_id_and_trade_hub_id( @eve_item, @trade_hub ).destroy
  #   create( :trade_order, user: @user, trade_hub: @trade_hub, eve_item: @eve_item )
  #   get price_advices_show_challenged_prices_url
  #   assert_response :success
  # end

  test 'should get empty places' do
    get price_advices_empty_places_url
    assert_response :success
  end

  test 'should show challenged prices with min prices' do
    create( :trade_order, user: @user, trade_hub: @trade_hub, eve_item: @eve_item )
    get price_advices_show_challenged_prices_url
    assert_response :success
  end

end
