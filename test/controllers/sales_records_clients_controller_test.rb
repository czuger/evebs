require 'test_helper'

class SalesRecordsClientsControllerTest < ActionController::TestCase

  def setup
    @sale_record = create( :sale_record )
  end

  test "should get show" do
    get :show, id: @sale_record.eve_client.id
    assert_response :success
  end

  test "should get index" do
    get :index
    assert_response :success
  end

end
