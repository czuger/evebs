OmniAuth.config.logger = Rails.logger

Rails.application.config.middleware.use OmniAuth::Builder do
  # provider :developer unless Rails.env.production?
  # Thanks to : https://coderwall.com/p/bsfitw/ruby-on-rails-4-authentication-with-facebook-and-omniauth
  provider :facebook, '1423903911250248', 'b20bfe70879536e219da6820b8aea962'
  provider :identity, on_failed_registration: lambda { |env|
    IdentitiesController.action(:new).call(env)
  }
end

OmniAuth.config.on_failure = Proc.new { |env|
  OmniAuth::FailureEndpoint.new(env).redirect_to_failure
}