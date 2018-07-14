require 'test_helper'

class ListItemsControllerTest < ActionDispatch::IntegrationTest

  def setup
    @user = create( :user, last_changes_in_choices: Time.now - 120 )
    post '/auth/developer/callback', params: { name: @user.name }
    @user.reload
  end

  test 'should get edit' do
    get edit_list_items_url
    assert_response :success
  end

  test 'should get update' do
    patch list_items_url, params: { items: { 1 => :dummy } }
    assert_redirected_to edit_list_items_url
  end

end
