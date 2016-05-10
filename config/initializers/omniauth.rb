OmniAuth.config.logger = Rails.logger

Rails.application.config.middleware.use OmniAuth::Builder do
  # provider :developer unless Rails.env.production?
  # Thanks to : https://coderwall.com/p/bsfitw/ruby-on-rails-4-authentication-with-facebook-and-omniauth



  if File.exists?( 'config/omniauth.yaml' )
    results = YAML.load( File.open( 'config/omniauth.yaml' ).read )

    results.each do |result|
      provider *result
    end

    provider :identity, on_failed_registration: lambda { |env|
      IdentitiesController.action(:new).call(env)
    }
  end

end

OmniAuth.config.on_failure = Proc.new { |env|
  OmniAuth::FailureEndpoint.new(env).redirect_to_failure
}
