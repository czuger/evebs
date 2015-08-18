require 'test_helper'

class SaleRecordsControllerTest < ActionController::TestCase

  def setup
    @sale_record = create( :sale_record )
  end

  test "should get show" do
    get :show
    assert_response :success
  end

  test "should get station_sums" do
    get :station_sums
    assert_response :success
  end

  test "should get items_sums" do
    get :items_sums
    assert_response :success
  end

  test "should get stations_items_sums" do
    get :stations_items_sums
    assert_response :success
  end

end
