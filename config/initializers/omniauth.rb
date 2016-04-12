OmniAuth.config.logger = Rails.logger

Rails.application.config.middleware.use OmniAuth::Builder do
  # provider :developer unless Rails.env.production?
  # Thanks to : https://coderwall.com/p/bsfitw/ruby-on-rails-4-authentication-with-facebook-and-omniauth

  provider :facebook, '1423903911250248', 'b20bfe70879536e219da6820b8aea962'
  provider :google_oauth2, '435800437430-kmgtgdlbr5jo53smnhiafe3cvvtbgglo.apps.googleusercontent.com', 'gjogipms3ECXLLSFv95VZZ48'
  provider :crest, '360a9dffb6fb4ade98945d9512c90f09', 'REyPAbCHUOw6fFanCDcdh4bz6jUpIk1tVWik22vA'

  provider :identity, on_failed_registration: lambda { |env|
    IdentitiesController.action(:new).call(env)
  }
end

OmniAuth.config.on_failure = Proc.new { |env|
  OmniAuth::FailureEndpoint.new(env).redirect_to_failure
}
