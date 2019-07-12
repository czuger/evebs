require 'simplecov'
SimpleCov.start 'rails'

ENV['RAILS_ENV'] ||= 'test'
require File.expand_path('../../config/environment', __FILE__)
require 'rails/test_help'

class ActiveSupport::TestCase
  # Setup all fixtures in test/fixtures/*.yml for all tests in alphabetical order.
  fixtures :all

  include FactoryBot::Syntax::Methods
  # Add more helper methods to be used by all tests here...
end

class ActionDispatch::IntegrationTest
  # This allows us to test jobs start in all controllers.
  include ActiveJob::TestHelper
end

require 'mocha/minitest'