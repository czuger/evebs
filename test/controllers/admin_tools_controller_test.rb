require 'test_helper'

class AdminToolsControllerTest < ActionDispatch::IntegrationTest

  # def setup
  #   @user = create( :user, last_changes_in_choices: Time.now - 120, region: @heimatar, admin: true )
  #   post '/auth/developer/callback', params: { name: @user.name }
  # end
  #
  # test 'should get show' do
  #   get admin_tools_url
  #   assert_response :success
  # end
  #
  # test 'should get items_users' do
  #   get items_users_admin_tools_url
  #   assert_response :success
  # end
  #
  # test 'should get crest_price_history_update' do
  #   get crest_price_history_update_admin_tools_url
  #   assert_response :success
  # end
  #
  # test 'should get min_prices_timings_overview' do
  #   get min_prices_timings_overview_admin_tools_url
  #   assert_response :success
  # end
  #
  # test 'should get min_prices_timings' do
  #   get min_prices_timings_admin_tools_url
  #   assert_response :success
  # end
  #
  # test 'should get activity' do
  #   get activity_admin_tools_url
  #   assert_response :success
  # end
  #
  # test 'non logged should not have access' do
  #   get signout_path
  #   get admin_tools_url
  #   assert_redirected_to new_sessions_url
  # end
  #
  # test 'non admin should not have access' do
  #   @user.update_attributes!( admin: false )
  #   get admin_tools_url
  #   assert_redirected_to denied_admin_tools_url
  # end

end
