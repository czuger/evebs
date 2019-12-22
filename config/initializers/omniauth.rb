OmniAuth.config.logger = Rails.logger

Rails.application.config.middleware.use OmniAuth::Builder do
  # provider :developer unless Rails.env.production?
  # Thanks to : https://coderwall.com/p/bsfitw/ruby-on-rails-4-authentication-with-facebook-and-omniauth

  id= File.exist?( 'config/omniauth.yaml' ) ? YAML.load_file( 'config/omniauth.yaml' ) : { esi: [] }
  client_id, secret_key = id[:esi]
  provider :eve_online_sso, client_id, secret_key, scope: 'esi-characters.read_blueprints.v1 esi-assets.read_assets.v1 esi-markets.read_character_orders.v1 esi-universe.read_structures.v1 esi-markets.structure_markets.v1'
end

OmniAuth.config.on_failure = Proc.new { |env|
  OmniAuth::FailureEndpoint.new(env).redirect_to_failure
}

if Rails.env.test?
  OmniAuth.config.full_host = 'http://localhost'
end
