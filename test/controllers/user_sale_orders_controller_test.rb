require 'test_helper'

class UserSaleOrdersControllerTest < ActionDispatch::IntegrationTest

  def setup
    @user = create( :user, sales_orders_show_margin_min: true )
    post '/auth/developer/callback', params: { name: @user.name }

    @blueprint = create( :blueprint )

    @eve_item = create( :inferno_fury_cruise_missile, blueprint_id: @blueprint.id )
    @trade_hub = create( :rens )
    # Sql::PricesAdvices.update
  end

  test 'should show challenged prices with min prices' do
    create( :user_sale_order, user: @user, trade_hub: @trade_hub, eve_item: @eve_item )
    get user_sales_orders_url
    assert_response :success
  end

  test 'should show challenged prices without min prices' do
    get user_sales_orders_url
    assert_response :success
  end

  test 'should start downloading my orders' do
    assert_enqueued_with(job: DownloadMyOrdersJob) do
      patch user_sales_orders_path
    end
    assert_redirected_to user_sales_orders_path
  end

end
