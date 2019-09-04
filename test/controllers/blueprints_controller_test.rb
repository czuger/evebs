require 'test_helper'

class BlueprintsControllerTest < ActionDispatch::IntegrationTest

  def setup
    esi_fake_login
  end

  test 'should show blueprints modifications list' do
    get blueprints_path
    assert_response :success
  end

  test 'should start downloading my blueprints' do
    assert_enqueued_with(job: DownloadMyBlueprintsJob) do
      patch blueprints_path
    end
    assert_redirected_to blueprints_path
  end

end