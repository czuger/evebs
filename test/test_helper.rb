# require 'simplecov'
# SimpleCov.start 'rails'

ENV['RAILS_ENV'] ||= 'test'
require File.expand_path('../../config/environment', __FILE__)
require 'rails/test_help'
require 'mocha/minitest'

class ActiveSupport::TestCase
  # Setup all fixtures in test/fixtures/*.yml for all tests in alphabetical order.
  # fixtures :all

  include FactoryBot::Syntax::Methods
  # Add more helper methods to be used by all tests here...

	def esi_fake_login
		OmniAuth.config.test_mode = true

		@user = create( :user )

		esi_auth_hash =
			{
				:provider => 'eve_online_sso',
				:uid => @user.uid,
				info: {
					name: 'Foo Bar',
					email: 'foo_bar@gmail.com',
					expires_on: (Time.now + 1.week).to_s
				},
				credentials: {
					token: 123456,
					expires_at: 'expire_time'
				}
			}

		OmniAuth.config.mock_auth[:eve_online_sso] = OmniAuth::AuthHash.new    esi_auth_hash

		post '/auth/eve_online_sso'
		follow_redirect!
	end

end

class ActionDispatch::IntegrationTest
  # This allows us to test jobs start in all controllers.
  include ActiveJob::TestHelper
end

