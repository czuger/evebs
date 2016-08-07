require 'test_helper'

class AdminToolsControllerTest < ActionController::TestCase

  def setup
    @user = create( :user, last_changes_in_choices: Time.now - 120, region: @heimatar, admin: true )
    session[:user_id] = @user.id
  end

  test "should get show" do
    get :show
    assert_response :success
  end

  test "should get items_users" do
    get :items_users
    assert_response :success
  end

  test "should get crest_price_history_update" do
    get :crest_price_history_update
    assert_response :success
  end

  test "should get min_prices_timings_overview" do
    get :min_prices_timings_overview
    assert_response :success
  end

  test "should get min_prices_timings" do
    get :min_prices_timings
    assert_response :success
  end

  test "should get activity" do
    get :activity
    assert_response :success
  end

end
