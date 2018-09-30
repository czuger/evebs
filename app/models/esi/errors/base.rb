class Esi::Errors::Base < RuntimeError

  def self.dispatch( exception )
    error = exception

    case exception.message
    when '504 Gateway Timeout'
      error = Esi::Errors::GatewayTimeout.new
    when '502 Bad Gateway'
      error = Esi::Errors::BadGateway.new
    when '403 Forbidden'
      error = Esi::Errors::Forbidden.new
    when '420 status code 420'
      error = Esi::Errors::ErrorLimited.new
    when '404 Not Found'
      error = Esi::Errors::NotFound.new
    when 'Net::OpenTimeout'
      error = Esi::Errors::OpenTimeout.new
    when 'SocketError'
      error = Esi::Errors::SocketError.new
    end

    error
  end

  def retry?
    false
  end

end