OmniAuth.config.logger = Rails.logger

Rails.application.config.middleware.use OmniAuth::Builder do
  # provider :developer unless Rails.env.production?
  # Thanks to : https://coderwall.com/p/bsfitw/ruby-on-rails-4-authentication-with-facebook-and-omniauth

  provider :developer if Rails.env.development? || Rails.env.staging?

  if File.exists?( 'config/omniauth.yaml' )
    results = YAML.load( File.open( 'config/omniauth.yaml' ).read )

    pp results
    client_id, secret_key = results[:esi]

    provider :eve_online_sso, client_id, secret_key, scope: 'esi-markets.read_character_orders.v1'
  end

end

OmniAuth.config.on_failure = Proc.new { |env|
  OmniAuth::FailureEndpoint.new(env).redirect_to_failure
}

if Rails.env.test?
  OmniAuth.config.full_host = 'http://localhost'
end
