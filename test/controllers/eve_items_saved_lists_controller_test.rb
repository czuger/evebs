require 'test_helper'

class EveItemsSavedListsControllerTest < ActionDispatch::IntegrationTest

  def setup
    esi_fake_login
  end

  test 'should get index' do
    get eve_items_saved_lists_url
    assert_response :success
  end

  test 'should get clear' do
    get eve_items_saved_lists_clear_url
    assert_redirected_to eve_items_saved_lists_url
  end

  test 'should get new' do
    get new_eve_items_saved_list_url
    assert_response :success
  end

  # test 'should load a saved list' do
  #   get eve_items_saved_list_load_url( 1 )
  #   assert_response :success
  # end

end
