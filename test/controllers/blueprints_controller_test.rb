require 'test_helper'

class BlueprintsControllerTest < ActionDispatch::IntegrationTest

  def setup
    # @component = create( :component_morphite )
    #
    @user = create( :user )
    post '/auth/developer/callback', params: { name: @user.name }
  end

  test 'should show blueprints modifications list' do
    get blueprints_path
    assert_response :success
  end

end
