require 'test_helper'

class JitaMarginsTest < ActionDispatch::IntegrationTest

  def setup
    # @component = create( :component_morphite )
    #
    # @user = create( :user )
    # post '/auth/developer/callback', params: { name: @user.name }
  end

  test 'should show front page' do
    get '/'
    assert_response :success
  end

end
