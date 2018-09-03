class Esi::Errors::Base < RuntimeError

  def self.dispatch( exception )
    case exception.message
    when '504 Gateway Timeout'
      raise Esi::Errors::GatewayTimeout
    when '502 Bad Gateway'
      raise Esi::Errors::BadGateway
    when '403 Forbidden'
      raise Esi::Errors::Forbidden
    when '420 status code 420'
      raise Esi::Errors::ErrorLimited
    when '404 Not Found'
      raise Esi::Errors::NotFound
    else
      raise exception
    end
  end

  def pause
    sleep 3
  end

  def error_hook
  end

end