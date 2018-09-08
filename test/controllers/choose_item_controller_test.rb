require 'test_helper'

class ChooseItemsControllerTest < ActionDispatch::IntegrationTest

  def setup
    @user = create( :user )
    post '/auth/developer/callback', params: { name: @user.name }

    @item = create( :inferno_fury_cruise_missile )
  end
  #
  # test 'should select an item' do
  #   post select_items_choose_items_url, params: { item: 'true', id: @item.id, check_state: 'false' }
  #   @user.eve_items.reload
  #   assert_difference '@user.reload.eve_items.reload.count' do
  #     post select_items_choose_items_url, params: { item: 'true', id: @item.id, check_state: 'true' }
  #   end
  # end

  # not working anyway
  # test 'should get edit' do
  #   get edit_choose_items_url
  #   assert_response :success
  # end
  #
  # test 'should redirect to new session path if not logged in' do
  #   get signout_url
  #   get edit_choose_items_url
  #   assert_redirected_to '/'
  # end

end
